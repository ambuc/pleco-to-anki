def is_cjk(character):
    # See https://stackoverflow.com/a/37311125.
    return any([start <= ord(character) <= end for start, end in [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215), (63744, 64255), (65072, 65103), (65381, 65500), (131072, 196607)]])