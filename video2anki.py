# 00
from absl import app
from absl import flags
from absl import logging
# 01
from pytube import YouTube
import os
# 02
import subprocess
# 03
import scenedetect
# 05
import cnocr
import pinyin
# 06
import csv
# 09
import sox

FLAGS = flags.FLAGS
flags.DEFINE_string("video", None,
                    "Full URL of the (YouTube) video to download.")
flags.DEFINE_string("anki_collection", None,
                    "Full path to Anki collection.media")
flags.DEFINE_string("output_csv_dir", None,
                    "Directory in which to write output csv")
flags.DEFINE_string(
    "crop_command", "in_w:in_h/3:0:1.9*in_h/3",
    "The crop syntax to use to extract the bottom part of the video, which contains the subtitles."
)


def flatten(t):
    return [item for sublist in t for item in sublist]


def main(argv):
    del argv
    if not FLAGS.video:
        raise app.Error("Must provide --video.")
    if not FLAGS.anki_collection:
        raise app.Error("Must provide --anki_collection.")
    if not FLAGS.output_csv_dir:
        raise app.Error("Must provide --output_csv_dir.")

    # 1. Download video.
    logging.info(f"01 [Downloading] {FLAGS.video}...")
    yt = YouTube(FLAGS.video)
    tmpdir = f"/tmp/{yt.video_id}"
    logging.info(f"01 [Downloading] {yt.title} ({yt.video_id}).")
    os.makedirs(tmpdir, exist_ok=True)
    download_path = yt.streams.get_highest_resolution().download(
        output_path=tmpdir)
    logging.info(f"01 [Downloading] wrote to {download_path}")
    # Now lives in /tmp/<id>/<title>.<format>

    # 2. Must produce a cropped version of the video suitable for cut
    # analysis.
    # ffmpeg -i hsk12.mp4 -filter:v "crop=in_w:in_h/3:0:1.9*in_h/3" -c:a copy hsk12-cropped.mp4
    cropped_path = os.path.join(tmpdir, "02_cropped.mp4")
    if os.path.isfile(cropped_path):
        logging.warning(
            f"02 [Cropping] Cropped file at {cropped_path} already exists, skipping..."
        )
    else:
        logging.info(f"02 [Cropping] Writing cropped video to {cropped_path}")
        # TODO make this crop flag-configurable.
        preview_crop_command = f'ffplay -i "{download_path}" -vf "crop={FLAGS.crop_command}"'
        logging.info(
            f"02 [Cropping] running preview for you: `{preview_crop_command}`")
        subprocess.call(preview_crop_command, shell=True)
        # TODO make this crop flag-configurable.
        crop_command = f'ffmpeg -i "{download_path}" -filter:v "crop={FLAGS.crop_command}" -c:a copy "{cropped_path}"'
        logging.info(f"02 [Cropping] running `{crop_command}`")
        subprocess.call(crop_command, shell=True)

    # 3. Must run scenedetect to figure out when this video cuts.
    # Create our video & scene managers, then add the detector.
    scenelist_csv_path = os.path.join(tmpdir, "03_scenelist.csv")
    images_dir = os.path.join(tmpdir, "03_images")
    if os.path.exists(images_dir):
        logging.warning(
            f"03 [SceneDetection] The directory {images_dir} already exists, skipping image extraction."
        )
    else:
        video_manager = scenedetect.VideoManager([cropped_path])
        scene_manager = scenedetect.SceneManager()
        # TODO make this threshold flag-configurable.
        scene_manager.add_detector(
            scenedetect.detectors.ContentDetector(threshold=1))
        # Improve processing speed by downscaling before processing.
        video_manager.set_downscale_factor()
        # Start the video manager and perform the scene detection.
        video_manager.start()
        logging.info("03 [SceneDetection] Detecting scenes")
        scene_manager.detect_scenes(frame_source=video_manager)
        scenelist = scene_manager.get_scene_list()
        logging.info(f"03 [SceneDetection] Found {len(scenelist)} scenes.")
        # Save images.
        os.makedirs(images_dir, exist_ok=True)
        logging.info(f"03 [SceneDetection] Saving images to {images_dir}...")
        # imagepaths_by_scenenum is a map from scene number to a list of filenames under |images_dir|.)
        imagepaths_by_scenenum = scenedetect.scene_manager.save_images(
            scenelist,
            video_manager,
            output_dir=images_dir,
            show_progress=True)
        with open(scenelist_csv_path, "w") as f:
            scenedetect.scene_manager.write_scene_list(f, scenelist)
        logging.info(
            f"03 [SceneDetection] Saving images to {images_dir}... Done.")
        for scene, image_paths in imagepaths_by_scenenum.items():
            # Leave only the middle keyframe of each scene.
            os.remove(os.path.join(images_dir, image_paths[0]))
            os.remove(os.path.join(images_dir, image_paths[2]))

    # 5. Perform OCR text reading on these image files.
    logging.info("05 [OCR]")
    cn = cnocr.cn_ocr.CnOcr()  # Yes, yes, I know.
    hanzi_dir = os.path.join(tmpdir, "05_hanzi")
    pinyin_dir = os.path.join(tmpdir, "05_pinyin")
    os.makedirs(hanzi_dir, exist_ok=True)
    os.makedirs(pinyin_dir, exist_ok=True)
    for (_, _, files) in os.walk(images_dir):
        num_scenes = len(files)
        files.sort()
        for i, file in enumerate(files):
            logging.info(f"05 [OCR] Processing {i}/{num_scenes}")

            hanzi_txt_path = os.path.join(hanzi_dir, f"{i}.txt")
            pinyin_txt_path = os.path.join(pinyin_dir, f"{i}.txt")

            if os.path.exists(hanzi_txt_path) and os.path.exists(
                    pinyin_txt_path):
                logging.warning(
                    f"05 [OCR] Skipping scene {i}, outputs {hanzi_txt_path} and {pinyin_txt_path} both already exist."
                )
            else:
                # hanzi is going to be a list of tuples: List[Tuple[List[char], float]]
                hanzi_obj = cn.ocr(
                    img_fp=os.path.join(tmpdir, "03_images", file))

                # TODO better strip punctuation and spacing
                hanzi_txt = ''.join(flatten([chrs for (chrs, _) in hanzi_obj]))
                hanzi_txt = hanzi_txt.strip(''.join([
                    'o',
                    ',',
                    '，',
                ]))

                with open(os.path.join(hanzi_dir, f"{i}.txt"), "w") as f:
                    f.write(hanzi_txt)

                pinyin_txt = pinyin.get(hanzi_txt, delimiter=" ").strip()

                with open(os.path.join(pinyin_dir, f"{i}.txt"), "w") as f:
                    f.write(pinyin_txt)

                logging.info(
                    f"05 [OCR] Scene {i}: Extracted: {pinyin_txt} :: {hanzi_txt}"
                )

    # 5b. Load OCR'd hanzi into memory.
    logging.info(f"05b [OCR] Loading hanzi into memory.")
    hanzi_by_scenenum = {}
    for (_, _, files) in os.walk(hanzi_dir):
        files.sort()
        for i, file in enumerate(files):
            # file is "/tmp/abc/hanzi/2.txt", so scene_num is 2
            scene_num = int(os.path.splitext(os.path.basename(file))[0])
            with open(os.path.join(hanzi_dir, file), "r") as f:
                hanzi_by_scenenum[scene_num] = f.read()
    # 5c. Load OCR'd pinyin into memory.
    logging.info(f"05c [OCR] Loading pinyin into memory.")
    pinyin_by_scenenum = {}
    for (_, _, files) in os.walk(pinyin_dir):
        files.sort()
        for i, file in enumerate(files):
            # file is "/tmp/abc/pinyin/2.txt", so scene_num is 2
            scene_num = int(os.path.splitext(os.path.basename(file))[0])
            with open(os.path.join(pinyin_dir, file), "r") as f:
                pinyin_by_scenenum[scene_num] = f.read()

    # 6. Load CSV from scenelist_csv_path
    logging.info("06 [CSV scenelist]")
    # Each row is a list of:
    #     0. scene number
    # 1,2,3. start frame, timecode, time(seconds)
    # 4,5,6. end frame, timecode, time(seconds)
    # 7,8,9. length (frames, timecode, seconds)
    scenes_list = []
    with open(scenelist_csv_path, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for i, row in enumerate(reader):
            if i <= 1:
                # first and second rows are junk: first row is cSep timestamps.  second row is headers.
                continue
            # third row onwards is  data.
            scenes_list.append(row)

    # mapping from scene_num to start_sec.
    startsec_by_scenenum = {}
    for [i, _, _, start_sec, _, _, _, _, _, _] in scenes_list:
        scene_num = int(i) - 1
        startsec_by_scenenum[scene_num] = start_sec

    # 7. Audio
    logging.info("07 [Audio]")
    # ffmpeg -i hsk12.mp4 -c copy hsk12-audio.m4a
    # ffmpeg -i hsk12-audio.m4a -c:a flac hsk12-flac.flac
    output_m4a_path = os.path.join(tmpdir, "07_audio.m4a")
    if os.path.exists(output_m4a_path):
        logging.warning(
            f"07 [Audio] Output m4a path {output_m4a_path} already exists, not writing."
        )
    else:
        extract_m4a_command = f'ffmpeg -i "{download_path}" -c copy "{output_m4a_path}"'
        subprocess.call(extract_m4a_command, shell=True)

    output_flac_path = os.path.join(tmpdir, "07_audio.flac")
    if os.path.exists(output_flac_path):
        logging.warning(
            f"07 [Audio] Output flac path {output_flac_path} already exists, not writing."
        )
    else:
        extract_flac_command = f'ffmpeg -i "{output_m4a_path}" -c:a flac "{output_flac_path}"'
        subprocess.call(extract_flac_command, shell=True)

    logging.info("08 [Dedup]")
    # We must go through each scene in scenes_list and, if the hanzi_txt is the same as that of the previous scene, we must join the scenes together (in-memory) to prepare for audio clipping.
    # List of [scene_number_first, start_sec, end_sec, all_scenes_list]
    # Example: [ 1, 1.0, 2.0, [1,2,3] ]
    scenes_deduped_list = []
    scenes_accounted_for = set()
    num_scenes = len(scenes_list)
    for [i, _, _, start_sec, _, _, end_sec, _, _, _] in scenes_list:
        # NB: hanzi and all files are 0-indexed. But scenes are 1-indexed in the CSV.
        scene_num = int(i) - 1
        if scene_num in scenes_accounted_for:
            continue
        joined_scenes = [scene_num]
        real_start_sec = float(start_sec)
        real_end_sec = float(end_sec)
        j = scene_num + 1
        while j < num_scenes and hanzi_by_scenenum[j] == hanzi_by_scenenum[
                scene_num]:
            joined_scenes.append(j)
            scenes_accounted_for.add(j)
            # Why 6? that's the index of `end_sec` in the scenes_list format. Sorry...
            real_end_sec = float(scenes_list[j][6])
            j += 1
        logging.info(
            f"08 [Dedup] Decided that scene {scene_num} should be joined with {joined_scenes}."
        )
        scene = [scene_num, real_start_sec, real_end_sec, joined_scenes]
        scenes_deduped_list.append(scene)
        scenes_accounted_for.add(scene_num)
    # print(scenes_deduped_list)

    logging.info("09 [Audio slice]")
    audio_dir = os.path.join(tmpdir, "09_audio_slices")
    os.makedirs(audio_dir, exist_ok=True)
    for [i, start_sec, end_sec, _] in scenes_deduped_list:
        output_trimmed_audio_path = os.path.join(audio_dir, f"{i}.flac")
        if os.path.exists(output_trimmed_audio_path):
            logging.warning(
                f"09 [Audio slice] Output trimmed path {output_trimmed_audio_path} already exists, not writing."
            )
        else:
            tfm = sox.Transformer()
            tfm.trim(start_sec, end_sec)
            # TODO explore further compression
            tfm.compand()
            success = tfm.build_file(output_flac_path,
                                     output_trimmed_audio_path)
            logging.info(f"09 [Audio slice] Wrote {i}: {success}")

    # 10. Write audio to Anki collection.
    logging.info("10 [Write to Anki]")
    for (_, _, files) in os.walk(audio_dir):
        files.sort()
        for file in files:
            scene_num = int(os.path.splitext(os.path.basename(file))[0])
            dest_file = os.path.join(FLAGS.anki_collection,
                                     f"{yt.video_id}-{scene_num:04}.flac")
            if os.path.exists(dest_file):
                logging.warning(
                    f"10 [Write to Anki] Not writing {dest_file}, already exists..."
                )
            else:
                copy_cmd = f'cp "{os.path.join(audio_dir, file)}" "{dest_file}"'
                subprocess.call(copy_cmd, shell=True)
                logging.info(f"10 [Write to Anki] Wrote to {dest_file}.")

    logging.info("11 [Write output csv]")
    # format: [sound:filepath.flac];hanzi;pinyin;sourceurl
    output_csv_rows = []
    for scene_num, _, _, _ in scenes_deduped_list:
        ankifile = f"{yt.video_id}-{scene_num:04}.flac"
        hanzi_txt = hanzi_by_scenenum[scene_num]
        pinyin_txt = pinyin_by_scenenum[scene_num]
        if hanzi_txt == "" or pinyin_txt == "":
            continue
        startsec = int(float(startsec_by_scenenum[scene_num]))
        sourceurl = f"{FLAGS.video}&t={startsec}s"
        row = [
            f"[sound:{ankifile}]",
            hanzi_txt,
            pinyin_txt,
            sourceurl,
        ]
        joinedrow = ';'.join(row)
        output_csv_rows.append(joinedrow)
        logging.info(f"11 [Write output csv] writing: {joinedrow}")
    output_csv_path = os.path.join(FLAGS.output_csv_dir, f"{yt.video_id}.csv")
    if os.path.exists(output_csv_path):
        logging.warning(
            f"11 [Write output csv] Not writing csv; already exists at {output_csv_path}."
        )
    else:
        with open(output_csv_path, "w") as f:
            f.write("\n".join(output_csv_rows))

    logging.info("DONE")


if __name__ == '__main__':
    app.run(main)
