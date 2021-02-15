# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet


def get_path_as_list(path):
    return path.split("/")


def get_path_from_section(section):
    return section[9:]


class Snippets(kp.Plugin):
    """
    Quickly copy user defined snippets to the clipboard.
    """

    SNIPPETS = "snippets"
    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    structure = {}

    def __init__(self):
        super().__init__()

    def on_start(self):
        self._read_config()

    def on_catalog(self):
        catalog = []

        for root_node in self.structure.keys():
            if root_node != self.SNIPPETS:
                catalog.append(
                    self.create_item(
                        category=kp.ItemCategory.REFERENCE,
                        label=root_node,
                        short_desc=root_node + " " + self.SNIPPETS,
                        target=root_node,
                        args_hint=kp.ItemArgsHint.REQUIRED,
                        hit_hint=kp.ItemHitHint.NOARGS,
                    )
                )
            else:
                catalog += self.structure[self.SNIPPETS][self.SNIPPETS]

        self.set_catalog(catalog)

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        if items_chain and (
            items_chain[0].category() != kp.ItemCategory.REFERENCE
            or items_chain[0].target() not in self.structure.keys()
        ):
            return

        path = [node.label() for node in items_chain]

        structure_ref = self.get_node_from_structure(path)
        nodes = structure_ref.keys()

        suggestions = []

        for node in nodes:
            if node != self.SNIPPETS:
                suggestions.append(
                    self.create_item(
                        category=kp.ItemCategory.REFERENCE,
                        label=node,
                        short_desc=node + " " + self.SNIPPETS,
                        target=node,
                        args_hint=kp.ItemArgsHint.REQUIRED,
                        hit_hint=kp.ItemHitHint.NOARGS,
                    )
                )

        if self.SNIPPETS in nodes:
            suggestions += structure_ref[self.SNIPPETS]

        user_input = user_input.strip()

        self.set_suggestions(
            suggestions,
            kp.Match.ANY if not user_input else kp.Match.FUZZY,
            kp.Sort.NONE if not user_input else kp.Sort.SCORE_DESC,
        )

    def on_execute(self, item, action):
        if item and item.category() == self.ITEMCAT_RESULT:
            kpu.set_clipboard(item.target())

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self._read_config()
            self.on_catalog()

    def _read_config(self):
        settings = self.load_settings()

        sections = [
            section
            for section in settings.sections()
            if section.lower().startswith(self.SNIPPETS)
        ]

        data = {}

        for section in sections:
            path = get_path_from_section(section)

            data[path] = {}

            snippets = settings.keys(section)
            for snippet_key in snippets:
                snippet_string = settings.get(snippet_key, section=section)
                if not len(snippet_string):
                    self.warn(
                        'Snippet "{}" does not have "string" value (or is empty). Ignored.'.format(
                            snippet_key
                        )
                    )
                    continue

                data[path][snippet_key] = snippet_string

        self.generate_folder_structure(data)

    def get_node_from_structure(self, path):
        structure_ref = self.structure
        for node in path:
            structure_ref = structure_ref[node]
        return structure_ref

    def set_node_in_structure(self, path, value):
        structure_ref = self.structure
        for node in path[:-1]:
            structure_ref = structure_ref.setdefault(node, {})
        structure_ref[path[-1]] = value

    def generate_folder_structure(self, data):
        self.structure.clear()
        self.add_path_to_structure(get_path_as_list(path) for path in data.keys())

        for path, snippets in data.items():
            path = get_path_as_list(path)

            self.set_node_in_structure(
                path, {self.SNIPPETS: self.create_result_set(snippets)}
            )

    def add_path_to_structure(self, paths):
        for path in paths:
            structure_ref = self.structure
            for node in path:
                if node not in structure_ref:
                    structure_ref[node] = {}
                structure_ref = structure_ref[node]

    def create_result_set(self, snippets):
        results = []

        for label, snippet in snippets.items():
            short_description = snippet.replace("\n", "↵")
            results.append(
                self.create_item(
                    category=self.ITEMCAT_RESULT,
                    label=label,
                    short_desc=short_description,
                    target=snippet,
                    args_hint=kp.ItemArgsHint.FORBIDDEN,
                    hit_hint=kp.ItemHitHint.IGNORE,
                )
            )

        return results
