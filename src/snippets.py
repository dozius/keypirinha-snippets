# Keypirinha launcher (keypirinha.com)

import os
import sys

package = os.path.join(os.path.dirname(__file__))
if package not in sys.path:
    sys.path.append(package)

import yaml

import keypirinha as kp
import keypirinha_util as kpu


class Snippets(kp.Plugin):
    """
    Quickly copy user defined snippets to the clipboard.
    """

    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    yaml_filepath = None
    yaml_data = {}

    def __init__(self):
        super().__init__()

    def on_start(self):
        self._read_config()

    def on_catalog(self):
        self._parse_yaml(self.yaml_filepath)
        self.set_catalog(self._catalog(self.yaml_data))

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        data = self.yaml_data
        for node in [node.label() for node in items_chain]:
            data = data[node]

        suggestions = self._catalog(data)

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
            self.on_catalog()


    def _read_config(self):
        settings = self.load_settings()

        if settings.has('yaml', section='main'):
            yaml_filename = settings.get('yaml', section='main')
            self.yaml_filepath = os.path.join(kp.user_config_dir(), yaml_filename)

            self.info('YAML file found: ', self.yaml_filepath)

            self._parse_yaml(self.yaml_filepath)
        else:
            self.err('YAML file not found')

    def _parse_yaml(self, file_path):
        self.info('Loading snippets...')
        with open(file_path, 'r', encoding='utf-8') as stream:
            try:
                self.yaml_data = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.err(e)
                return
        
        self.info(self.yaml_data)

    def _catalog(self, data):
        suggestions = []

        for key, val in data.items():
            if type(val) is dict:
                suggestions.append(
                    self.create_item(
                        category=kp.ItemCategory.REFERENCE,
                        label=key,
                        short_desc=key + ' snippets',
                        target=key,
                        args_hint=kp.ItemArgsHint.REQUIRED,
                        hit_hint=kp.ItemHitHint.NOARGS,
                    )
                )
            else:
                suggestions.append(
                    self.create_item(
                        category=self.ITEMCAT_RESULT,
                        label=key,
                        short_desc=val.replace("\n", "↵"),
                        target=val,
                        args_hint=kp.ItemArgsHint.FORBIDDEN,
                        hit_hint=kp.ItemHitHint.IGNORE,
                    )
                )
        
        return suggestions
