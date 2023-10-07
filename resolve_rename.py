import re

fu = bmd.scriptapp('Fusion')
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

def this_pj():
    resolve = bmd.scriptapp('Resolve')
    pj_manager = resolve.GetProjectManager()
    current_pj = pj_manager.GetCurrentProject()
    return current_pj

def this_timeline():
    return this_pj().GetCurrentTimeline()

def get_all_track_clips(track_num=2, track_type='video'):
    return this_timeline().GetItemsInTrack(track_type, track_num)

def get_all_track_names(timeline, track_type='video'):
    track_count = int(this_timeline().GetTrackCount(track_type))
    track_names = []
    for i in range(1, track_count + 1):
        track_names.append('[{}] {}'.format(i, this_timeline().GetTrackName(track_type, i)))
    return track_names

def get_video_track_number_by_current_item():
    timeline = this_timeline()
    current_item = timeline.GetCurrentVideoItem()
    track_count = int(timeline.GetTrackCount('video'))
    current_track = None
    for i in range(1, track_count + 1):
        all_itms = timeline.GetItemsInTrack('video', i)
        if current_item in all_itms:
            current_track = i
            break
    return current_track

clipcolor_names = [
    'Orange',
    'Apricot',
    'Yellow',
    'Lime',
    'Olive',
    'Green',
    'Teal',
    'Navy',
    'Blue',
    'Purple',
    'Violet',
    'Pink',
    'Tan',
    'Beige',
    'Brown',
    'Chocolate'
]

rename_types = [
    'Sequential',
    'Search and Replace'
]

sequential_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.Label({"Text": "Name Template:", "Alignment": {"AlignLeft": True}, "Weight": 0.1,}),
            ui.LineEdit({"ID": 'name_template', "Text": "sh_#", "PlaceholderText": "sh_#"}),
        ]),
        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.Label({"Text": 'From',  "Weight": 0}),
            ui.SpinBox({"ID": 'from', "Value": 10, "Minimum": 0, "Maximum": 100000, "SingleStep": 1}),
            ui.HGap(),
            ui.Label({"Text": 'Step',  "Weight": 0}),
            ui.SpinBox({"ID": 'step', "Value": 10, "Minimum": 1, "Maximum": 100000, "SingleStep": 1}),
            ui.HGap(),
            ui.Label({"Text": 'Padding',  "Weight": 0}),
            ui.SpinBox({"ID": 'padding', "Value": 3, "Minimum": 0, "Maximum": 10, "SingleStep": 1}),
        ]),
    ]),
])

search_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.Label({"Text": "Search:", "Weight": 0.2, "Alignment": {"AlignLeft": True}, "Weight": 0.1,}),
            ui.LineEdit({"ID": 'search', "Text": "^(.*)(\.\[.*\].exr)$"}),
        ]),
        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.Label({"Text": "Replace:", "Weight": 0.2,"Alignment": {"AlignLeft": True}, "Weight": 0.1,}),
            ui.LineEdit({"ID": 'replace', "Text": "\\1"}),
            ui.CheckBox({"ID": 'do_regex', "Weight": 0.1, "Text": "Regex", "Alignment": {"AlignRight": True}, "Checked": True, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
        ]),
    ]),
])


selection_group = ui.HGroup({"Spacing": 5, "Weight": 0},[
    ui.VGroup({"Spacing": 5, "Weight": 1},[
        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.Label({"Text": "Rename Type:", "Alignment": {"AlignLeft": True}, "Weight": 0.1,}),
            ui.ComboBox({"ID": 'rename_type', "Alignment": {"AlignLeft": True}}),
        ]),
        ui.Label({"StyleSheet": "max-height: 3px;"}),
        ui.Label({"StyleSheet": "max-height: 1px; background-color: rgb(10,10,10)"}),

        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.CheckBox({"ID": 'rename_by_track', "Text": "Only Rename Track:", "Alignment": {"AlignRight": True}, "Checked": True, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
            ui.ComboBox({"ID": 'track_names'})
        ]),
        ui.HGroup({"Spacing": 5, "Weight": 0},[
            ui.CheckBox({"ID": 'rename_by_color', "Text": "Rename Only Color:", "Checked": True, "AutoExclusive": True, "Checkable": True, "Events": {"Toggled": True}}),
            ui.ComboBox({"ID": 'clip_colors', }),
        ]),
        ui.Label({"StyleSheet": "max-height: 3px;"}),
        ui.Label({"StyleSheet": "max-height: 1px; background-color: rgb(10,10,10)"}),
        sequential_group,
        search_group,
    ])
])

window_01 = ui.VGroup([
    ui.HGroup({"Spacing": 1},
        [
            ui.VGroup({"Spacing": 15, "Weight": 3},[
                ui.Label({"StyleSheet": "max-height: 5px;"}),
                selection_group,
                ui.Button({"ID": "Run", "Text": "Rename", "Weight": 0, "Enabled": True}),
                ui.Label({"ID": 'status', "Text": "", "Alignment": {"AlignCenter": True}, 'ReadOnly': True}),
                ui.Label({"StyleSheet": "max-height: 5px;"}),
            ]),       
        ]
    )
])

dlg = disp.AddWindow({ 
                        'WindowTitle': 'Batch Renamer', 
                        'ID': 'MyWin',
                        'Geometry': [ 
                                    800, 500, # position when starting
                                    400, 400 # width, height
                         ], 
                        },
    window_01)
 
itm = dlg.GetItems()
itm['clip_colors'].AddItems(clipcolor_names)
itm['track_names'].AddItems(get_all_track_names(this_timeline()))
itm['rename_type'].AddItems(rename_types)

def _exit(ev):
    disp.ExitLoop()

def _run(ev):
    print('I run!')
    clip_list = _filter()
    rename(clip_list)

def get_track_clip_list(clip_list, timeline, track_number, filter_color):

    all_track_clips = timeline.GetItemsInTrack('video', track_number)
    track_name = timeline.GetTrackName('video', track_number)
    for i in all_track_clips:
        tl_clip = all_track_clips[i]
        clip_color = tl_clip.GetClipColor()
        media_pool_item = tl_clip.GetMediaPoolItem()
        ignore = False
        if filter_color:
            if filter_color != clip_color:
                ignore = True
        if not ignore:
            clip_info = {
                'item': tl_clip,
                'pool_item': media_pool_item,
                'track_number': track_number,
                'track_name': track_name,
                'name': tl_clip.GetName(),
                'color': clip_color,
                'in': tl_clip.GetStart(),
                'out': tl_clip.GetEnd(),
                'head': tl_clip.GetLeftOffset(),
                'tail': tl_clip.GetRightOffset(),
                'duration': tl_clip.GetDuration(),
                'resolution': media_pool_item.GetClipProperty('Resolution') if media_pool_item is not None else 'Null',
                'pool_name': media_pool_item.GetClipProperty('Clip Name') if media_pool_item is not None else 'Null'
            }
            clip_list.append(clip_info)

    return clip_list

def get_clip_list(track_number=1, filter_color="Orange"):
    
    timeline = this_timeline()
    all_clips = []

    if track_number:
        all_clips = get_track_clip_list(all_clips, timeline, track_number, filter_color)
    else:
        track_count = int(timeline.GetTrackCount('video'))
        for current_track_number in range(1, track_count + 1):
            all_clips = get_track_clip_list(all_clips, timeline, current_track_number, filter_color)

    # sort by in and track number
    return sorted(all_clips, key=lambda k: (float(k['in']), k['track_number']))


def rename_sequential(clip_list):
    
    # clean up rename
    for one_clip in clip_list:
        one_clip['new_name'] = one_clip['name']

    temp = str(itm['name_template'].Text)
    # reduce to one hash
    template = '#'.join([s for s in temp.split('#') if s != ''])
    _s = template.split('#')
    template_before = template
    template_after = ''
    if _s and len(_s)>=2:
        template_before = _s[0]
        template_after = _s[1]

    cnt_from = int(itm['from'].Value)
    cnt_step = int(itm['step'].Value)
    cnt_pad = int(itm['padding'].Value)

    for one_clip in clip_list:
        num = (clip_list.index(one_clip) * cnt_step) + cnt_from
        one_clip['new_name'] = template_before + str(num).zfill(cnt_pad) + template_after

    return clip_list

def do_one_regex(content, in_search, in_replace):

    try:
        compiled = re.compile(in_search)
    except:
        print('regex error')

    if in_replace and in_replace != '':
        # replace
        if in_replace.startswith("lambda "):
            try:
                _eval = eval(str(in_replace))
            except:
                _eval = in_replace
            try:
                result = re.sub(compiled, _eval, content)
            except:
                result = None
        else:
            try:
                result = compiled.match(content).expand(in_replace)
            except:
                result = None
    else:
        try:
            m = re.search(in_search, content)
        except:
            pass
        if m:
            try:
                result = content
            except:
                result = None
        else:
            result = None
    return result

def rename_search(clip_list):

    in_search = str(itm['search'].Text)
    in_replace = str(itm['replace'].Text)
    is_regex = bool(itm['do_regex'].Checked)

    # clean up rename
    for one_clip in clip_list:
        one_clip['new_name'] = one_clip['name']

    if is_regex:
        try:
            compiled = re.compile(in_search)
            for one_clip in clip_list:
                one_clip['new_name'] = do_one_regex(one_clip['name'], in_search, in_replace)
                if one_clip['new_name'] is None:
                    one_clip['new_name'] = one_clip['name']
        except:
            print('regex error')
    else:
        for one_clip in clip_list:
            one_clip['new_name'] = one_clip['name'].replace(in_search, in_replace)

    return clip_list

def rename(clip_list):

    for one_clip in clip_list:
        # this works for pool item, but not for timelineitem
        one_clip['pool_item'].SetClipProperty('Clip Name', one_clip['new_name'])

        # doesn't work for timeline item
        #one_clip['item'].SetName(one_clip['new_name'])
        #one_clip['item'].SetClipProperty('Clip Name', one_clip['new_name'])
        #one_clip['item'].SetProperty('Clip Name', one_clip['new_name'])
    
def _filter(*ev):

    filter_color = bool(itm['rename_by_color'].Checked)
    filtered_color = itm['clip_colors'].CurrentText
    if not filter_color:
        filtered_color = None

    filter_track = bool(itm['rename_by_track'].Checked)
    filtered_track_name = itm['track_names'].CurrentText
    filtered_track_number = get_all_track_names(this_timeline()).index(filtered_track_name) + 1
    if not filter_track:
        filtered_track_name = None
        filtered_track_number = None

    clip_list = get_clip_list(filtered_track_number, filtered_color)
    dlg.Find('status').Text = "Found {} clips to rename.".format(len(clip_list))

    what_rename = itm['rename_type'].CurrentText
    if what_rename == 'Sequential':
        clip_list = rename_sequential(clip_list)
    elif what_rename == 'Search and Replace':
        clip_list = rename_search(clip_list)

    return clip_list

def _swap_search(ev):

    what_rename = itm['rename_type'].CurrentText
    if what_rename == 'Sequential':
        sequential_group.Show()
        search_group.Hide()
    elif what_rename == 'Search and Replace':
        sequential_group.Hide()
        search_group.Show()



dlg.On.MyWin.Close = _exit
dlg.On["Run"].Clicked = _run
dlg.On['rename_by_track'].Toggled = _filter
dlg.On['track_names'].CurrentIndexChanged = _filter
dlg.On['rename_by_color'].Toggled = _filter
dlg.On['clip_colors'].CurrentIndexChanged = _filter
dlg.On['rename_type'].CurrentIndexChanged = _swap_search

dlg.Show()
disp.RunLoop()
dlg.Hide()