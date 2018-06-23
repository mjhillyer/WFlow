from django.contrib import admin
from django import forms
from django.utils.html import escape as escape_html

from .models import \
	AppSource, AppInstance, Module, ModuleQuestion, ModuleAsset, \
	Task, TaskAnswer, TaskAnswerHistory, \
	InstrumentationEvent

class AppSourceSpecWidget(forms.Widget):
    fields = [
		("type",
		 "Source Type",
		 forms.Select(choices=[
		 	("null", "Null Source"),
		 	("local", "Local Directory"),
		 	("git-web", "Git Repository over HTTPS (Public Repository)"),
		 	("git-ssh", "Git Repository over SSH (Private Repository)"),
		 	("github", "GitHub Repository using Github API")]),
		 "What kind of app source is it?",
		 None),
		("url-web",
		 "URL",
		 forms.TextInput(),
		 "The https: URL to a public git repository, e.g. https://github.com/GovReady/govready-q.",
		 { "git-web" }),
		("url-ssh",
		 "SSH URL",
		 forms.TextInput(),
		 "The SSH URL to a private git repository, e.g. git@github.com:GovReady/govready-q.git.",
		 { "git-ssh" }),
		("repo",
		 "Repository",
		 forms.TextInput(),
		 "The repository name in 'organization/repository' format.",
		 { "github" }),
		("branch",
		 "Branch",
		 forms.TextInput(),
		 "The name of the branch in the repository to read apps from. Leave blank to read from the default branch, which is usually 'master'.",
		 { "git-web", "git-ssh" }),
		("path",
		 "Path",
		 forms.TextInput(),
		 "The path to the apps. For local directory AppSources, the local directory path. Otherwise the path within the repository, or blank if the apps are at the repository root.",
		 { "local", "git-web", "git-ssh", "github" }),
		("ssh_key",
		 "SSH Key",
		 forms.Textarea(attrs={"rows": 3 }),
		 "Paste an SSH private key here and send the public key to the repository owner. For GitHub and Gitlab repositories, add the public key as a deploy key in the repository's settings.",
		 { "git-ssh" }),
		("_remaining_",
		 "Other Parameters",
		 forms.Textarea(attrs={"rows": 2 }),
		 "Other parameters specified in YAML.",
		 None),
	]

    def render(self, name, value, attrs=None):
    	# For some reason we get the JSON value as a string. Unless we override Form.clean(),
    	# and then strangely we get a dict.
    	if isinstance(value, (str, type(None))):
    		import json, collections
    		value = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(value or "{}")

    	# The 'url' key is represented by two different widgets
    	# depending on if the URL is an HTTP or SSH URL.
    	if value.get("type") == "git" and isinstance(value.get("url"), str):
	    	import re
	    	if value["url"].startswith("https:") or value["url"].startswith("http:"):
	    		value["type"] = "git-web"
	    		value["url-web"] = value["url"]
	    		del value["url"]
	    	elif re.match(r"(?P<user>[a-z_][a-z0-9_-]{0,29})@(?P<host>\S+):(?P<path>\S+)", value["url"]):
	    		# This is a really cursory regex for one form of SSH URL
	    		# that git recognizes, as user@host:path. There are
	    		# remarkably no real requirements for a SSH username
	    		# --- the regex here is tighter than is really required.
	    		# But it's usually just "git" anyway.
	    		value["type"] = "git-ssh"
	    		value["url-ssh"] = value["url"]
	    		del value["url"]
	    	else:
	    		raise ValueError(value)

    	def make_widget(key, label, widget, help_text, show_for_types):
    	    if key != "_remaining_":
    	    	if key in value:
    	    		val = value[key]
    	    		del value[key] # only the unrecognized keys are left at the end
    	    	else:
    	    		val = ""
    	    elif len(value) == 0:
    	    	# Nothing unrecognized.
    	    	val = ""
    	    else:
    	    	# Serialize unrecognized keys in YAML.
    	        import rtyaml
    	        val = rtyaml.dump(value)
    	    return """
    	    	<div style="clear: both; padding-bottom: .75em" class="{}">
    	        	<label for="id_{}_{}">{}:</label>
    	    		{}
    	    		<p class="help">{}</p>
    	    	</div>""".format(
    	    		(
    	    			"show_if_type "
    	    			 + " ".join(("show_if_type_" + s) for s in show_for_types)
    	    			 if show_for_types
    	    			 else ""
    	    		),
		            escape_html(name),
		            key,
		            escape_html(label),
		            widget.render(name + "_" + key, val),
		            escape_html(help_text or ""),
		            )
    	
    	# Widgets
    	ret = "\n\n".join(make_widget(*args) for args in self.fields)

    	# Click handler to only show fields that are appropriate for
    	# the selected AppSource type.
    	ret += """
    	<script>
    		django.jQuery("select[name=spec_type]")
    			.change(function() {
    				django.jQuery(".show_if_type").hide()
    				django.jQuery(".show_if_type_" + this.value).show()
    			})
    			.change() // init
    	</script>
    	"""
    	return ret

    def value_from_datadict(self, data, files, name):
    	# Start with the extra data.
    	import rtyaml, collections
    	value = rtyaml.load(data[name + "__remaining_"]) or collections.OrderedDict()

    	# Add other values.
    	for key, label, widget, help_text, show_for_types in self.fields:
    		if key == "_remaining_": continue # already got this
    		val = data.get(name + "_" + key)
    		if val:
    			value[key] = val

    	# Map some data.
    	if value.get("type") == "git-web":
    		value["type"] = "git"
    		value["url"] = str(value.get("url-web"))
    		del value["url-web"]
    	elif value.get("type") == "git-ssh":
    		value["type"] = "git"
    		value["url"] = str(value.get("url-ssh"))
    		del value["url-ssh"]

    	return value

class ApprovedAppsList(forms.Widget):
	def __init__(self, appsource):
		super().__init__()
		self.appsource = appsource

	def render(self, name, value, attrs=None):
		# For some reason we get the JSON value as a string. Unless we override Form.clean(),
		# and then strangely we get a dict.
		if isinstance(value, str):
			import json, collections
			value = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(value or "{}")
		if not isinstance(value, dict):
			value = {}

		# Get all of the apps to list from the AppSource instance, if this
		# form is associated with an existing AppSource instance.
		from .app_source_connections import AppSourceConnectionError
		applist = []
		seen_apps = set()
		if self.appsource:
			try:
				with self.appsource.open() as conn:
					for app in conn.list_apps():
						applist.append((app.name, app.get_catalog_info()))
						seen_apps.add(app.name)
			except AppSourceConnectionError:
				pass

		# Add in any apps that are no longer in the AppSource but have a
		# value stored.
		for appkey in value:
			if appkey in seen_apps: continue
			applist.append((appkey, {
				"title": appkey,
				"published": None,
			}))

		# Construct widget.
		import html
		widget = "<table><tbody>\n"
		for appname, appinfo in applist:
			widget += "<tr>"
			widget += "<td style='padding: 14px'>"
			widget += html.escape(appinfo["title"])
			widget += "</td><td>"
			widget += forms.Select(choices=[
			 	("", "{} (Default)".format(
			 		("Unpublished" if appinfo["published"] == "unpublished" else "Published")
			 	)),
			 	("unpublished", "Unpublished"),
			 	("published", "Published"),
			 	])\
				.render(name + "__" + appname, value.get(appname))
			widget += "</td></tr>\n"
		widget += "</tobdy></table>\n"

		return widget

	def value_from_datadict(self, data, files, name):
		from collections import OrderedDict
		ret = {}
		for key, value in data.items():
			if not key.startswith(name + "__"): continue
			key = key[len(name)+2:]
			if value == "": continue # reset to default
			ret[key] = value
		return ret

class AppSourceAdminForm(forms.ModelForm):
	class Meta:
		labels = {
			"available_to_all": "Apps from this source are available to all organizations"
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Override the widget for 'spec' to break out the connection
		# settings into separate fields.
		self.fields['spec'].widget = AppSourceSpecWidget()
		self.fields['spec'].label = "How is this AppSource accessed?"
		self.fields['spec'].help_text = None

		# Override the widget for 'approved_apps' to break out the apps
		# into separate widgets.
		self.fields['approved_apps'].widget = ApprovedAppsList(kwargs.get("instance"))
		self.fields['approved_apps'].help_text = None

	def clean(self):
		# Do form field valudation.
		super(AppSourceAdminForm, self).clean()

		if not self.errors:
			# Validate that the AppSource can actually connect to the source.
			try:
				with AppSource(slug=self.cleaned_data["slug"], spec=self.cleaned_data["spec"]).open() as store:
					pass
			except Exception as e:
				raise forms.ValidationError(str(e))


class AppSourceAdmin(admin.ModelAdmin):
	form = AppSourceAdminForm # customize spec and approved_apps widgets
	list_display = ('slug', 'source', 'flags')
	filter_horizontal = ('available_to_orgs',)
	readonly_fields = ('is_system_source',)
	def source(self, obj):
		return obj.get_description()
	def flags(self, obj):
		flags = []
		if obj.is_system_source: flags.append("SYSTEM")
		return ", ".join(flags)

class AppInstanceAdmin(admin.ModelAdmin):
	list_display = ('appname', 'version_number', 'version_name', 'source', 'system_app')
	list_filter = ('source', 'system_app')
	raw_id_fields = ('source', 'asset_files',)
	readonly_fields = ('asset_files','asset_paths')

class ModuleAdmin(admin.ModelAdmin):
	list_display = ('id', 'source', 'app_', 'module_name', 'created')
	list_filter = ('source',)
	raw_id_fields = ('source', 'app', 'superseded_by')
	def app_(self, obj): return "{} [{}]".format(obj.app.appname, obj.app.id) if obj.app else "(not in an app)"

class ModuleQuestionAdmin(admin.ModelAdmin):
	raw_id_fields = ('module', 'answer_type_module')

class ModuleAssetAdmin(admin.ModelAdmin):
	list_display = ('id', 'source', 'content_hash', 'created')
	raw_id_fields = ('source',)
	readonly_fields = ('source','content_hash','file')

class TaskAdmin(admin.ModelAdmin):
	list_display = ('title', 'organization_and_project', 'editor', 'module', 'is_finished', 'submodule_of', 'created')
	raw_id_fields = ('project', 'editor', 'module')
	readonly_fields = ('module', 'invitation_history')
	search_fields = ('project__organization__name', 'editor__username', 'editor__email', 'module__key')
	def submodule_of(self, obj):
		return obj.is_answer_to_unique()
	def organization_and_project(self, obj):
		return obj.project.organization_and_title()

class TaskAnswerAdmin(admin.ModelAdmin):
	list_display = ('question', 'task', '_project', 'created')
	raw_id_fields = ('task',)
	readonly_fields = ('task', 'question')
	search_fields = ('task__project__organization__name', 'task__module__key')
	fieldsets = [(None, { "fields": ('task', 'question') }),
	             (None, { "fields": ('notes',) }),
	             (None, { "fields": ('extra',) }), ]
	def _project(self, obj): return obj.task.project

class TaskAnswerHistoryAdmin(admin.ModelAdmin):
	list_display = ('created', 'taskanswer', 'answered_by', 'is_latest')
	raw_id_fields = ('taskanswer', 'answered_by', 'answered_by_task')
	readonly_fields = ('taskanswer', 'answered_by', 'created')
	search_fields = ('taskanswer__task__project__organization__name', 'taskanswer__task__module__key', 'answered_by__username', 'answered_by__email')
	fieldsets = [(None, { "fields": ('created', 'taskanswer', 'answered_by') }),
	             (None, { "fields": ('stored_value', 'stored_encoding', 'cleared') }),
	             (None, { "fields": ('extra',) }) ]
	def answer(self, obj): return obj.get_answer_display()

class InstrumentationEventAdmin(admin.ModelAdmin):
	list_display = ('event_time', 'event_type', 'user', 'event_value', 'task')
	raw_id_fields = ('project', 'user', 'module', 'question', 'task', 'answer')
	readonly_fields = ('event_time', 'event_type', 'event_value', 'user', 'module', 'question', 'task', 'answer')

admin.site.register(AppSource, AppSourceAdmin)
admin.site.register(AppInstance, AppInstanceAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ModuleQuestion, ModuleQuestionAdmin)
admin.site.register(ModuleAsset, ModuleAssetAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAnswer, TaskAnswerAdmin)
admin.site.register(TaskAnswerHistory, TaskAnswerHistoryAdmin)
admin.site.register(InstrumentationEvent, InstrumentationEventAdmin)
