# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet

class Snippets(kp.Plugin):
    """
    Quickly copy user defined snippets to the clipboard.
    """
    DEFAULT_KEYWORD = "snip"
    CONFIG_SECTION_SNIPPETS = "snippet"
    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    keyword = DEFAULT_KEYWORD
    snippets = []

    def __init__(self):
        super().__init__()

    def on_start(self):
        self._read_config()

    def on_catalog(self):
        self.set_catalog([self.create_item(
            category = kp.ItemCategory.KEYWORD,
            label = self.keyword,
            short_desc = "Copy a snippet to the clipboard",
            target = self.keyword,
            args_hint = kp.ItemArgsHint.REQUIRED,
            hit_hint = kp.ItemHitHint.NOARGS)])

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        if items_chain and (
                items_chain[0].category() != kp.ItemCategory.KEYWORD or
                items_chain[0].target() != self.keyword):
            return

        user_input = user_input.strip()

        self.set_suggestions(
            self.snippets,
            kp.Match.ANY if not user_input else kp.Match.FUZZY,
            kp.Sort.LABEL_ASC if not user_input else kp.Sort.SCORE_DESC)


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
        self.snippets.clear()
        settings = self.load_settings()

        self.keyword = settings.get("keyword", section = "main", fallback = self.DEFAULT_KEYWORD)

        for section in settings.sections():
            if section.lower().startswith(self.CONFIG_SECTION_SNIPPETS + "/"):
                snippet_label = section[len(self.CONFIG_SECTION_SNIPPETS) + 1:].strip()
            else:
                continue

            if not len(snippet_label):
                self.warn('Ignoring empty snippet name (section "{}").'.format(section))
                continue

            if any(x.label().lower() == snippet_label.lower() for x in self.snippets):
                self.warn('Ignoring duplicated snippet "{}" defined in section "{}".'.format(snippet_label, section))
                continue

            snippet_string = settings.get("string", section = section)
            if not len(snippet_string):
                self.warn('Snippet "{}" does not have "string" value (or is empty). Ignored.'.format(snippet_label))
                continue

            self.snippets.append(self.create_item(
                category = self.ITEMCAT_RESULT,
                label = snippet_label,
                short_desc = snippet_string,
                target = snippet_string,
                args_hint = kp.ItemArgsHint.FORBIDDEN,
                hit_hint = kp.ItemHitHint.IGNORE))
