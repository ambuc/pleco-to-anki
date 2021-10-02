from absl import logging
from third_party import ids
from typing import Text, Optional, Callable, Any, Dict, TypeVar, Tuple, cast, List, Callable, Iterable
import dataclasses
import networkx as nx
import re

# new types
LookupCb = Callable[[Text], Optional[Text]]

# Type variables for |_build_paths|.
K = TypeVar("K")
V = TypeVar("V")

# data
_VERBS = frozenset("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")

# The ids.txt database uses a string like  "^⿲冫虫𮫙$(K)" to list an IDS
# (ideographic description sequence) and its list of valid regions.
_IDS_AND_REGIONS_REGEX = re.compile(
    r"\^(?P<ids>\S+)\$\s*(\((?P<regions>[A-Z]+)\))?\s*")


# dataclasses

@dataclasses.dataclass(frozen=True)
class Shape:
    width: float
    height: float
    x_offset: float
    y_offset: float

    def portion(self, s: "Shape") -> "Shape":
        return Shape(width=self.width * s.width,
                     height=self.height * s.height,
                     x_offset=self.x_offset + (s.x_offset * self.width),
                     y_offset=self.y_offset + (s.y_offset * self.height))


UnitSquare = Shape(width=1, height=1, x_offset=0, y_offset=0)
LeftHalf = Shape(width=0.5, height=1, x_offset=0, y_offset=0)
RightHalf = Shape(width=0.5, height=1, x_offset=0.5, y_offset=0)
TopHalf = Shape(width=1, height=0.5, x_offset=0, y_offset=0)
BottomHalf = Shape(width=1, height=0.5, x_offset=0, y_offset=0.5)


@dataclasses.dataclass
class VisualMetadata:
    shape: Shape
    parent: Text


_SHAPES_BY_VERB = {
    "⿰": [LeftHalf, RightHalf],
    "⿲": [
        Shape(0.33, 1.0, 0.0, 0.0),
        Shape(0.33, 1.0, 0.33, 0.0),
        Shape(0.33, 1.0, 0.66, 0.0)
    ],
    "⿱": [TopHalf, BottomHalf],
    "⿳": [
        Shape(1.0, 0.33, 0.0, 0.0),
        Shape(1.0, 0.33, 0.0, 0.33),
        Shape(1.0, 0.33, 0.0, 0.66)
    ],
    # Both shapes are full-size. This is the tricky one and should probably
    # not be relied upon.
    "⿻": [UnitSquare, UnitSquare],
    # +----+----+----+----+
    # |    |    |    |    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    |    |    |    |
    # +----+----+----+----+
    "⿴": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.5, 0.5, 0.25, 0.25),
    ],
    # +----+----+----+----+
    # |    |    |    |    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    "⿵": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.5, 0.75, 0.25, 0.25),
    ],
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    XXXXXXXXXXX    |
    # +----XXXXXXXXXXX----+
    # |    |    |    |    |
    # +----+----+----+----+
    "⿶": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.5, 0.75, 0.25, 0.0),
    ],
    # +----+----+----+----+
    # |    |    |    |    |
    # +----XXXXXXXXXXXXXXXX
    # |    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # |    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # |    |    |    |    |
    # +----+----+----+----+
    "⿷": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.75, 0.5, 0.25, 0.25),
    ],
    # +----+----+----+----+
    # |    |    |    |    |
    # +----XXXXXXXXXXXXXXXX
    # |    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # |    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # |    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    "⿸": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.75, 0.75, 0.25, 0.25),
    ],
    # +----+----+----+----+
    # |    |    |    |    |
    # XXXXXXXXXXXXXXXX----+
    # XXXXXXXXXXXXXXXX    |
    # XXXXXXXXXXXXXXXX----+
    # XXXXXXXXXXXXXXXX    |
    # XXXXXXXXXXXXXXXX----+
    # XXXXXXXXXXXXXXXX    |
    # XXXXXXXXXXXXXXXX----+
    "⿹": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.75, 0.75, 0.0, 0.25),
    ],
    # +----XXXXXXXXXXXXXXXX
    # +    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # +    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # +    XXXXXXXXXXXXXXXX
    # +----XXXXXXXXXXXXXXXX
    # +    |    |    |    |
    # +----+----+----+----+
    "⿺": [
        Shape(1.0, 1.0, 0.0, 0.0),
        Shape(0.75, 0.75, 0.25, 0.0),
    ]
}


def _fast_is_cjk(x) -> bool:
    # Clauses, in order:
    # (1) CJK Unified Ideographs
    # (2) CJK Unified Ideographs Extension A
    # (3) CJK Unified Ideographs Extension B
    # (4) CJK Unified Ideographs Extension C
    # (5) CJK Unified Ideographs Extension D
    # (6) CJK Unified Ideographs Extension E
    # (7) CJK Unified Ideographs Extension F
    # (8) CJK Unified Ideographs Extension G
    return (0x4E00 <= x <= 0x9FFF) or (0x3400 <= x <= 0x4DBF) or (
        0x20000 <= x <= 0x2A5DF) or (0x2A700 <= x <= 0x2B73F) or (
            0x2B740 <= x <= 0x2B81F) or (0x2B820 <= x <= 0x2CEAF) or (
                0x2CEB0 <= x <= 0x2EBEF) or (0x30000 <= x <= 0x3134F)


@dataclasses.dataclass
class IdeographicSequence:
    character: Text
    decomposition: Text

    def _expand(self, decomposition: Text, lookup_cb: LookupCb):
        output = []
        for c in decomposition:
            if not _fast_is_cjk(ord(c)):
                # Must be a verb, push this onto the stack as-is.
                output.append(c)
                continue

            expanded = lookup_cb(c)
            if expanded is None:
                # No decomposition, push this character onto the stack as-is
                output.append(c)
                continue
            elif expanded != c:
                # If the character had an expansion, let's recurse before
                # appending.
                output.extend(self._expand(expanded, lookup_cb))
            else:
                # Otherwise the character can be pushed as-is.
                output.append(c)
        return "".join(output)


def _get_decomposition(
        text_in: Text) -> Optional[Tuple[Text]]:
    match = _IDS_AND_REGIONS_REGEX.match(text_in)
    if match is None:
        logging.debug("Didn't match compiled regex.")
        return None
    d = match.groupdict()
    return d["ids"]


def _build_paths(g: nx.DiGraph, node: Any, data_lookup: Callable[[
                 Dict[K, V]], V], accumulator: Callable[[V, V], V]):
    result = {}
    for succ in g.successors(node):
        if succ == node:
            continue
        result[succ] = data_lookup(g.get_edge_data(node, succ))
        for subnode, d in _build_paths(g, succ, data_lookup,
                                       accumulator).items():
            result[subnode] = accumulator(d, result[succ])
    return result


def _parse(text_in: Text) -> Optional[IdeographicSequence]:
    split_input = text_in.rstrip().split("\t")

    if len(split_input) < 3:
        logging.debug("Input must be at least three columns.")
        return None

    character = split_input[1]
    decomposition = _get_decomposition(split_input[2])
    if decomposition is None:
        logging.debug("Invalid input: %s", text_in)
        return None

    return IdeographicSequence(character, decomposition)


class Decomposer():
    def __init__(self):

        # Graph where the nodes are unicode characters and the edges are "contains"
        # such that successors(尔) = [...你...]., and predecessors(你) = [亻,尔].
        # So, insert with self._graph.add_edge( "亻", "你" )
        #                 self._graph.add_edge( "尔", "你" )
        self._graph = nx.DiGraph()

        with open(ids.PATH_TO_IDS_TXT, encoding="UTF-8") as fp:
            for line in fp:
                # Ignore comments
                if line.startswith("#"):
                    continue
                # TODO(ambuc): ids.txt uses:
                # {1}, {2}, etc. to represent unencoded components.
                # ↔         as a mirror operator, i.e. to represent a component without
                #           a Unicode encoding, but whose mirror does have a Unicode
                #           encoding.
                # ↷        as a rotation operator, i.e. to represent a component
                #           without a Unicode encoding, but whose 180deg rotation does
                #           have a Unicode encoding.
                # 〾        as a variation indicator. We should try to handle these.
                # ?, ？     ids.txt uses these to represent an unencodable component.
                # We should probably try to handle these edge cases.
                elif re.search("[{}↔↷〾?？]", line):
                    continue

                maybe_parsed_set = _parse(str(line))
                if maybe_parsed_set is not None:
                    self.insert(maybe_parsed_set)

    def characters(self) -> Iterable[Text]:
        return [
            node for node in self._graph.nodes()
            if list(self._graph.predecessors(node))
        ]

    def contains(self, character: Text) -> bool:
        if character not in self._graph.nodes():
            return False
        return bool(list(self._graph.predecessors(character)))

    def decompose(self, character: Text) -> IdeographicSequence:
        if character not in self._graph.nodes:
            raise ValueError(character)
        if "sq" not in self._graph.nodes[character]:
            raise ValueError(character)
        if not list(self._graph.predecessors(character)):
            raise ValueError(character)
        return self._graph.nodes[character]["sq"]

    def insert(self, sequence: IdeographicSequence) -> bool:
        char = sequence.character
        decomp = sequence.decomposition
        i = self._traverse_sequence(
            0, char, decomp, VisualMetadata(
                shape=UnitSquare, parent=char))

        if i < len(decomp):
            logging.debug("Something went wrong trying to parse decomp: %s",
                          ",".join(["U+%04x" % ord(o) for o in decomp]))
            return False

        self._graph.add_node(char, sq=sequence)
        return True

    def _get_with_component(self, component: Text) -> Iterable[Tuple[Text]]:
        return _build_paths(g=self._graph,
                            node=component,
                            data_lookup=lambda m: m["metadata"].shape,
                            accumulator=lambda a, b: a.portion(b)).items()

    def get_component(self, component: Text) -> List[Text]:
        return [c for c, _ in self._get_with_component(component)]

    def _traverse_sequence(
            self,
            i: int,
            character: Text,
            decomposition: Text,
            metadata: VisualMetadata) -> int:
        if i >= len(decomposition):
            return i

        head = decomposition[i]
        i += 1

        # If there is no decomposition, we've reached a fundamental particle and
        # can't go any further.
        if head not in _VERBS:
            self._graph.add_edge(head, character, metadata=metadata)
            return i

        for arg in _SHAPES_BY_VERB[head]:
            i = self._traverse_sequence(
                i, character, decomposition,
                VisualMetadata(shape=metadata.shape.portion(arg),
                               parent=character))

        return i
