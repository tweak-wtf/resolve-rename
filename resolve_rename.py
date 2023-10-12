import re
import utils

# ? why can't i import bmd here? linting errors are annoying 🙃
# import bmd


# NOTE: everything that gets invoked via a callback in resolve passes in
#       and informational dict containing data about the event
#       EXAMPLE:
#       {'what': 'Clicked', 'when': 247013.234, 'sender': <BlackmagicFusion.PyRemoteObject object at 0x000000000329DE90>, 'modifiers': {'ShiftModifier': False, 'ControlModifier': True, 'AltModifier': False, 'MetaModifier': False, 'KeypadModifier': False, 'GroupSwitchModifier': False}, 'who': 'Run', 'window': 'MyWin', 'On': False}


class Renamer:
    def __init__(self, fu) -> None:
        self.fu = fu

    def run(self, event=None):
        if event:
            print(event)
        print("Renamer renaming things...")


class UI:
    def __init__(self, fu) -> None:
        self.fu = fu
        self.renamer = Renamer(fu)
        self.ui_manager = self.fu.UIManager
        self.ui_dispatcher = bmd.UIDispatcher(self.ui_manager)

        self.rename_types = ["Sequential", "Search and Replace"]
        self.clipcolor_names = [
            "Orange",
            "Apricot",
            "Yellow",
            "Lime",
            "Olive",
            "Green",
            "Teal",
            "Navy",
            "Blue",
            "Purple",
            "Violet",
            "Pink",
            "Tan",
            "Beige",
            "Brown",
            "Chocolate",
        ]

        self.create_ui()
        self.init_ui_defaults()
        self.init_ui_callbacks()

        self.ui_items = self.main_win.GetItems()

    def create_ui(self):
        self.sequential_grp = self.ui_manager.HGroup(
            {"Spacing": 5, "Weight": 0},
            [
                self.ui_manager.VGroup(
                    {"Spacing": 5, "Weight": 1},
                    [
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.Label(
                                    {
                                        "Text": "Name Template:",
                                        "Alignment": {"AlignLeft": True},
                                        "Weight": 0.1,
                                    }
                                ),
                                self.ui_manager.LineEdit(
                                    {
                                        "ID": "name_template",
                                        "Text": "sh_#",
                                        "PlaceholderText": "sh_#",
                                    }
                                ),
                            ],
                        ),
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.Label({"Text": "From", "Weight": 0}),
                                self.ui_manager.SpinBox(
                                    {
                                        "ID": "from",
                                        "Value": 10,
                                        "Minimum": 0,
                                        "Maximum": 100000,
                                        "SingleStep": 1,
                                    }
                                ),
                                self.ui_manager.HGap(),
                                self.ui_manager.Label({"Text": "Step", "Weight": 0}),
                                self.ui_manager.SpinBox(
                                    {
                                        "ID": "step",
                                        "Value": 10,
                                        "Minimum": 1,
                                        "Maximum": 100000,
                                        "SingleStep": 1,
                                    }
                                ),
                                self.ui_manager.HGap(),
                                self.ui_manager.Label({"Text": "Padding", "Weight": 0}),
                                self.ui_manager.SpinBox(
                                    {
                                        "ID": "padding",
                                        "Value": 3,
                                        "Minimum": 0,
                                        "Maximum": 10,
                                        "SingleStep": 1,
                                    }
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
        self.search_grp = self.ui_manager.HGroup(
            {"Spacing": 5, "Weight": 0},
            [
                self.ui_manager.VGroup(
                    {"Spacing": 5, "Weight": 1},
                    [
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.Label(
                                    {
                                        "Text": "Search:",
                                        "Weight": 0.2,
                                        "Alignment": {"AlignLeft": True},
                                        "Weight": 0.1,
                                    }
                                ),
                                self.ui_manager.LineEdit(
                                    {"ID": "search", "Text": "^(.*)(\.\[.*\].exr)$"}
                                ),
                            ],
                        ),
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.Label(
                                    {
                                        "Text": "Replace:",
                                        "Weight": 0.2,
                                        "Alignment": {"AlignLeft": True},
                                        "Weight": 0.1,
                                    }
                                ),
                                self.ui_manager.LineEdit(
                                    {"ID": "replace", "Text": "\\1"}
                                ),
                                self.ui_manager.CheckBox(
                                    {
                                        "ID": "do_regex",
                                        "Weight": 0.1,
                                        "Text": "Regex",
                                        "Alignment": {"AlignRight": True},
                                        "Checked": True,
                                        "AutoExclusive": True,
                                        "Checkable": True,
                                        "Events": {"Toggled": True},
                                    }
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
        self.selection_grp = self.ui_manager.HGroup(
            {"Spacing": 5, "Weight": 0},
            [
                self.ui_manager.VGroup(
                    {"Spacing": 5, "Weight": 1},
                    [
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.Label(
                                    {
                                        "Text": "Rename Type:",
                                        "Alignment": {"AlignLeft": True},
                                        "Weight": 0.1,
                                    }
                                ),
                                self.ui_manager.ComboBox(
                                    {
                                        "ID": "rename_type",
                                        "Alignment": {"AlignLeft": True},
                                    }
                                ),
                            ],
                        ),
                        self.ui_manager.Label({"StyleSheet": "max-height: 3px;"}),
                        self.ui_manager.Label(
                            {
                                "StyleSheet": "max-height: 1px; background-color: rgb(10,10,10)"
                            }
                        ),
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.CheckBox(
                                    {
                                        "ID": "rename_by_track",
                                        "Text": "Only Rename Track:",
                                        "Alignment": {"AlignRight": True},
                                        "Checked": True,
                                        "AutoExclusive": True,
                                        "Checkable": True,
                                        "Events": {"Toggled": True},
                                    }
                                ),
                                self.ui_manager.ComboBox({"ID": "track_names"}),
                            ],
                        ),
                        self.ui_manager.HGroup(
                            {"Spacing": 5, "Weight": 0},
                            [
                                self.ui_manager.CheckBox(
                                    {
                                        "ID": "rename_by_color",
                                        "Text": "Rename Only Color:",
                                        "Checked": True,
                                        "AutoExclusive": True,
                                        "Checkable": True,
                                        "Events": {"Toggled": True},
                                    }
                                ),
                                self.ui_manager.ComboBox(
                                    {
                                        "ID": "clip_colors",
                                    }
                                ),
                            ],
                        ),
                        self.ui_manager.Label({"StyleSheet": "max-height: 3px;"}),
                        self.ui_manager.Label(
                            {
                                "StyleSheet": "max-height: 1px; background-color: rgb(10,10,10)"
                            }
                        ),
                        self.sequential_grp,
                        self.search_grp,
                    ],
                )
            ],
        )
        self.vlayout = self.ui_manager.VGroup(
            [
                self.ui_manager.HGroup(
                    {"Spacing": 1},
                    [
                        self.ui_manager.VGroup(
                            {"Spacing": 15, "Weight": 3},
                            [
                                self.ui_manager.Label(
                                    {"StyleSheet": "max-height: 5px;"}
                                ),
                                self.selection_grp,
                                self.ui_manager.Button(
                                    {
                                        "ID": "run",
                                        "Text": "Rename",
                                        "Weight": 0,
                                        "Enabled": True,
                                    }
                                ),
                                self.ui_manager.Label(
                                    {
                                        "ID": "status",
                                        "Text": "",
                                        "Alignment": {"AlignCenter": True},
                                        "ReadOnly": True,
                                    }
                                ),
                                self.ui_manager.Label(
                                    {"StyleSheet": "max-height: 5px;"}
                                ),
                            ],
                        ),
                    ],
                )
            ]
        )
        self.main_win = self.ui_dispatcher.AddWindow(
            {
                "WindowTitle": "Batch Renamer",
                "ID": "main_win",
                "Geometry": [
                    800,
                    500,
                    400,
                    400,
                ],  # position when starting  # width, height
            },
            self.vlayout,
        )

    def init_ui_defaults(self):
        items = self.main_win.GetItems()
        print(items)
        items["clip_colors"].AddItems(self.clipcolor_names)
        # items["track_names"].AddItems(get_all_track_names(this_timeline()))
        items["rename_type"].AddItems(self.rename_types)

    def init_ui_callbacks(self):
        self.main_win.On.MyWin.Close = lambda e: self.destroy(event=e)
        # fmt: off
        self.main_win.On["Run"].Clicked = lambda e: self.renamer.run(event=e)  # writing the code i wish i had
        # fmt: on
        # self.main_win.On["rename_by_track"].Toggled = _filter
        # self.main_win.On["track_names"].CurrentIndexChanged = _filter
        # self.main_win.On["rename_by_color"].Toggled = _filter
        # self.main_win.On["clip_colors"].CurrentIndexChanged = _filter
        # self.main_win.On["rename_type"].CurrentIndexChanged = _swap_search

    def destroy(self, event=None):
        if event:
            print(event)
        self.ui_dispatcher.ExitLoop()

    def start(self):
        self.main_win.Show()
        self.ui_dispatcher.RunLoop()
        self.main_win.Hide()


app = UI(bmd.scriptapp("Fusion"))
app.start()
