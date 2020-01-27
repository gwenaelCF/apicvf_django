include $(MFEXT_HOME)/opt/misc/share/plugin.mk

custom::
	@# your custom build directives here




collectstatic:
	python manage.py collectstatic --no-input

