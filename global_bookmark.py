import sublime, sublime_plugin


class GlobalBookmarkUtil:
    global_bookmark_index = 0
    @classmethod
    def saveToSettings(cls, view):
        regions = view.get_regions("global_bookmarks")
        current_file = view.file_name()
        marks = []
        for r in regions:
            line, col = view.rowcol(r.begin())
            marks.append(line)
        settings = sublime.load_settings("GlobalBookmarks.sublime-settings")
        all_marks = settings.get("marks", {})
        diff = False
        if len(marks):
            if not current_file in all_marks or all_marks[current_file] != marks:
                diff = True
                all_marks[current_file] = marks
        else:
            if current_file in all_marks:
                del all_marks[current_file]
                diff = True
        if diff:
            settings.set("marks", all_marks)
            settings.set("dirty", True)

    @classmethod
    def save(cls, view):
        GlobalBookmarkUtil.saveToSettings(view)
        settings = sublime.load_settings("GlobalBookmarks.sublime-settings")
        if settings.get("dirty"):
            settings.erase("dirty")
            sublime.save_settings("GlobalBookmarks.sublime-settings")


class GlobalBookmarkToggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        current_file = view.file_name()
        regions = view.get_regions("global_bookmarks")
        for s in view.sel():
            in_region = False
            for idx in range(len(regions)):
                r = regions[idx]
                if view.full_line(r).contains(s.begin()):
                    in_region = True
                    del regions[idx]
                    break
            if not in_region:
                regions.append(sublime.Region(s.begin(), s.begin()))

        view.add_regions("global_bookmarks", regions, "mark", "bookmark",
            sublime.HIDDEN | sublime.PERSISTENT)

        GlobalBookmarkUtil.saveToSettings(view)

class GlobalBookmarkClearCommand(sublime_plugin.WindowCommand):
    def run(self):
        orig_view = self.window.active_view()
        orig_group = self.window.active_group()
        settings = sublime.load_settings("GlobalBookmarks.sublime-settings")
        all_marks = settings.get("marks", {})
        for filename in all_marks:
            view = self.window.open_file(filename, sublime.TRANSIENT)
            view.erase_regions("global_bookmarks")
        settings.set("marks", {})
        settings.erase("dirty")
        # Save
        sublime.save_settings("GlobalBookmarks.sublime-settings")
        self.window.focus_group(orig_group)
        self.window.focus_view(orig_view)

class GlobalBookmarkNextCommand(sublime_plugin.WindowCommand):
    def openview(self, desired_idx):
        settings = sublime.load_settings("GlobalBookmarks.sublime-settings")
        all_marks = settings.get("marks", {})
        to_open = False
        idx = 0
        for filename in all_marks:
            for linenum in all_marks[filename]:
                #print filename + ":" + str(linenum+1) + " " + str(idx) + " " + str(desired_idx)
                if (not to_open) or (idx == desired_idx):
                    # Default to first file, or if idx is matched
                    to_open = filename + ":" + str(linenum + 1)
                    GlobalBookmarkUtil.global_bookmark_index = idx
                idx = idx + 1

        views = self.window.views()
        view = self.window.open_file(to_open, sublime.ENCODED_POSITION)
        for vv in views:
            if vv.id() == view.id():
                # was already open
                return view
        return

    def run(self):
        desired_idx = GlobalBookmarkUtil.global_bookmark_index + 1
        view = self.openview(desired_idx)
        if view:
            GlobalBookmarkUtil.saveToSettings(view) # Refresh in case they've moved
            self.openview(desired_idx)

    def is_enabled(self):
        settings = sublime.load_settings("GlobalBookmarks.sublime-settings")
        all_marks = settings.get("marks", {})
        return len(all_marks) > 0



class GlobalBookmarkRestore(sublime_plugin.EventListener):
    # restore on load for new opened tabs or previews.
    def on_load(self, view):
        settings = sublime.load_settings("GlobalBookmarks.sublime-settings")
        all_marks = settings.get("marks", {})
        current_file = view.file_name()
        if current_file in all_marks:
            marks = all_marks[current_file]
            regions = []
            for r in marks:
                p = view.text_point(r, 0)
                regions.append(sublime.Region(p, p))

            view.add_regions("global_bookmarks", regions, "mark", "bookmark",
                sublime.HIDDEN | sublime.PERSISTENT)

    def on_post_save(self, view):
        # Saving a file, if it has any modified bookmarks, save them!
        GlobalBookmarkUtil.save(view)
    def on_close(self, view):
        # May have added a bookmark, but made no modifications
        if not view.is_dirty():
            GlobalBookmarkUtil.save(view)
