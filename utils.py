def get_mediapoolitem():
    pass


def this_pj():
    resolve = bmd.scriptapp("Resolve")
    pj_manager = resolve.GetProjectManager()
    current_pj = pj_manager.GetCurrentProject()
    return current_pj


def this_timeline():
    return this_pj().GetCurrentTimeline()


def get_all_track_clips(track_num=2, track_type="video"):
    return this_timeline().GetItemsInTrack(track_type, track_num)


def get_all_track_names(timeline, track_type="video"):
    track_count = int(this_timeline().GetTrackCount(track_type))
    track_names = []
    for i in range(1, track_count + 1):
        track_names.append(
            "[{}] {}".format(i, this_timeline().GetTrackName(track_type, i))
        )
    return track_names


def get_video_track_number_by_current_item():
    timeline = this_timeline()
    current_item = timeline.GetCurrentVideoItem()
    track_count = int(timeline.GetTrackCount("video"))
    current_track = None
    for i in range(1, track_count + 1):
        all_itms = timeline.GetItemsInTrack("video", i)
        if current_item in all_itms:
            current_track = i
            break
    return current_track


def _exit(ev):
    disp.ExitLoop()


def _run(ev):
    print("I run!")
    clip_list = _filter()
    rename(clip_list)


def get_track_clip_list(clip_list, timeline, track_number, filter_color):

    all_track_clips = timeline.GetItemsInTrack("video", track_number)
    track_name = timeline.GetTrackName("video", track_number)
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
                "item": tl_clip,
                "pool_item": media_pool_item,
                "track_number": track_number,
                "track_name": track_name,
                "name": tl_clip.GetName(),
                "color": clip_color,
                "in": tl_clip.GetStart(),
                "out": tl_clip.GetEnd(),
                "head": tl_clip.GetLeftOffset(),
                "tail": tl_clip.GetRightOffset(),
                "duration": tl_clip.GetDuration(),
                "resolution": media_pool_item.GetClipProperty("Resolution")
                if media_pool_item is not None
                else "Null",
                "pool_name": media_pool_item.GetClipProperty("Clip Name")
                if media_pool_item is not None
                else "Null",
            }
            clip_list.append(clip_info)

    return clip_list


def get_clip_list(track_number=1, filter_color="Orange"):

    timeline = this_timeline()
    all_clips = []

    if track_number:
        all_clips = get_track_clip_list(all_clips, timeline, track_number, filter_color)
    else:
        track_count = int(timeline.GetTrackCount("video"))
        for current_track_number in range(1, track_count + 1):
            all_clips = get_track_clip_list(
                all_clips, timeline, current_track_number, filter_color
            )

    # sort by in and track number
    return sorted(all_clips, key=lambda k: (float(k["in"]), k["track_number"]))


def rename_sequential(clip_list):

    # clean up rename
    for one_clip in clip_list:
        one_clip["new_name"] = one_clip["name"]

    temp = str(itm["name_template"].Text)
    # reduce to one hash
    template = "#".join([s for s in temp.split("#") if s != ""])
    _s = template.split("#")
    template_before = template
    template_after = ""
    if _s and len(_s) >= 2:
        template_before = _s[0]
        template_after = _s[1]

    cnt_from = int(itm["from"].Value)
    cnt_step = int(itm["step"].Value)
    cnt_pad = int(itm["padding"].Value)

    for one_clip in clip_list:
        num = (clip_list.index(one_clip) * cnt_step) + cnt_from
        one_clip["new_name"] = (
            template_before + str(num).zfill(cnt_pad) + template_after
        )

    return clip_list


def do_one_regex(content, in_search, in_replace):

    try:
        compiled = re.compile(in_search)
    except:
        print("regex error")

    if in_replace and in_replace != "":
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

    in_search = str(itm["search"].Text)
    in_replace = str(itm["replace"].Text)
    is_regex = bool(itm["do_regex"].Checked)

    # clean up rename
    for one_clip in clip_list:
        one_clip["new_name"] = one_clip["name"]

    if is_regex:
        try:
            compiled = re.compile(in_search)
            for one_clip in clip_list:
                one_clip["new_name"] = do_one_regex(
                    one_clip["name"], in_search, in_replace
                )
                if one_clip["new_name"] is None:
                    one_clip["new_name"] = one_clip["name"]
        except:
            print("regex error")
    else:
        for one_clip in clip_list:
            one_clip["new_name"] = one_clip["name"].replace(in_search, in_replace)

    return clip_list


def rename(clip_list):
    # one_clip: MediaPoolItem
    for one_clip in clip_list:
        # this works for pool item, but not for timelineitem
        one_clip["pool_item"].SetClipProperty("Clip Name", one_clip["new_name"])
        # shot_metadata = one_clip['pool_item'].SetMetadata("Shot", one_clip["new_name"])
        # print(f"Set Shot Metadata: {shot_metadata}")
        # clipname_metadata = one_clip['pool_item'].SetMetadata("Name", "%Shot%")
        # print(f"Set Clip Name Metadata: {clipname_metadata}")
        # all_meta = one_clip["item"].GetMetadata()  # only returns metadata currently set
        # print(all_meta)
        # doesn't work for timeline item
        # one_clip['item'].SetName(one_clip['new_name'])
        # one_clip['item'].SetClipProperty('Clip Name', one_clip['new_name'])
        # one_clip['item'].SetProperty('Clip Name', one_clip['new_name'])


def _filter(*ev):

    filter_color = bool(itm["rename_by_color"].Checked)
    filtered_color = itm["clip_colors"].CurrentText
    if not filter_color:
        filtered_color = None

    filter_track = bool(itm["rename_by_track"].Checked)
    filtered_track_name = itm["track_names"].CurrentText
    filtered_track_number = (
        get_all_track_names(this_timeline()).index(filtered_track_name) + 1
    )
    if not filter_track:
        filtered_track_name = None
        filtered_track_number = None

    clip_list = get_clip_list(filtered_track_number, filtered_color)
    dlg.Find("status").Text = "Found {} clips to rename.".format(len(clip_list))

    what_rename = itm["rename_type"].CurrentText
    if what_rename == "Sequential":
        clip_list = rename_sequential(clip_list)
    elif what_rename == "Search and Replace":
        clip_list = rename_search(clip_list)

    return clip_list


def _swap_search(ev):

    what_rename = itm["rename_type"].CurrentText
    if what_rename == "Sequential":
        sequential_group.Show()
        search_group.Hide()
    elif what_rename == "Search and Replace":
        sequential_group.Hide()
        search_group.Show()
