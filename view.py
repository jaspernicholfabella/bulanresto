from flask import redirect,url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView,expose
from flask_login import current_user
from flask_admin import form
from config import config_data


class UserModelView(ModelView):
    can_delete = False
    page_size = 50
    create_modal = True
    edit_modal=True

    l1 = ['user','restaurant','admin']
    l2 = []
    for i in range(0, len(l1)):
        l2.append((l1[i], l1[i]))
    form_choices = {
        'access': l2
    }

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.access == 'admin':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class RestaurantsModelView(ModelView):
    can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True

    # column_exclude_list = ['content',]
    form_excluded_columns=['slug',]

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = str(model.useraccount)

    def _list_thumbnail(view, context, model, name):
        print(f'name: {name}')
        if name == 'image':
            return model.image
        else:
            return ''

    column_formatters = {
        'image': _list_thumbnail,
    }
    form_extra_fields = {
        'image': form.ImageUploadField('Image', base_path=config_data["image_file_path"], thumbnail_size=(100, 100, True)),
    }

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.access == 'admin':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class MenuItemsModelView(ModelView):
    # can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True
    # column_exclude_list = ['slug',]
    form_excluded_columns=['slug',]

    def _list_thumbnail(view, context, model, name):
        if name == 'image':
            return model.image
        else:
            return ''

    column_formatters = {
        'image': _list_thumbnail,
    }
    form_extra_fields = {
        'image': form.ImageUploadField('Image', base_path=config_data["image_file_path"], thumbnail_size=(100, 100, True)),
    }

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = str(current_user.name)

    def get_query(self):
        return self.session.query(self.model).filter(self.model.slug == current_user.name)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'restaurant':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class RestaurantSignupModelView(ModelView):
    can_create=False
    can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True
    form_excluded_columns=['name','address','owner','email','attached_files','date']

    def get_query(self):
        return self.session.query(self.model).filter(self.model.approved == False)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'admin':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return Truepyt

class DeliveryModelView(ModelView):
    can_create=False
    can_delete=False
    page_size = 50
    create_modal = True
    edit_modal = True
    column_exclude_list = ['slug', ]
    form_excluded_columns=['userid','slug','cartitems''date','total']

    def get_query(self):
        return self.session.query(self.model).filter(self.model.delivered == False).filter(self.model.slug == current_user.name)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'restaurant':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True

class DeliveryModelView2(ModelView):
    can_create=False
    can_delete=False
    can_edit=False
    page_size = 50
    create_modal = True
    edit_modal = True
    column_exclude_list = ['slug', ]
    form_excluded_columns=['userid','slug','cartitems''date','total','delivered']


    def get_query(self):
        return self.session.query(self.model).filter(self.model.delivered == True).filter(self.model.slug == current_user.name)

    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.access == 'restaurant':
                return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
        return True