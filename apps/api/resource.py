#encoding:utf-8
from apps.core.models import *
from django.contrib.auth.models import User
from tastypie.resources import ModelResource , ALL , ALL_WITH_RELATIONS 
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest 
from tastypie import fields
from django.core import serializers
from django.db.models import Q , F
from datetime import date 

# Usuario Datos

#class UsuarioDatosResource(ModelResource):
	#usuario = fields.ForeignKey("apps.api.resource.UsuarioResource", 'usuario'    ,  null = True , full = True )          
#	class Meta: 
#		queryset = UsuarioDatos.objects.all()
#		resource_name ='usuario'
#		authorization= Authorization()     

class UsuarioResource(ModelResource): 

	class Meta:
		queryset = User.objects.all().order_by("-date_joined") 
		excludes = ['password' , 'last_login','is_superuser', 'email', 'date_joined'  ,'is_active', 'is_staff',] 



class UsersResource(ModelResource):

	user = fields.ForeignKey("apps.api.resource.UsuarioResource",  full = True , attribute = 'user') 

  	class Meta:

	    object_class = User
	    queryset = AdminCreatedUsers.objects.all()
	    allowed_methods = ['get']
	    resource_name = 'users'
	    
  	def dehydrate(self , bundle):

		bundle.data["img"] = "https://s3.amazonaws.com/pinffiles/unknown.png"
		

		return bundle
	
	def get_object_list(self, request):

		 return super(UsersResource, self).get_object_list(request).filter( admin = request.user)


# ***********************************************************************************************************************
# ***********************************************************************************************************************
# ******************************************* SIGN UP**************************************************************
# ***********************************************************************************************************************
# ***********************************************************************************************************************


class UserSignUpResource(ModelResource):

  class Meta:
    object_class = User
    queryset = User.objects.all()
    allowed_methods = ['post']
    include_resource_uri = False
    resource_name = 'newuser'
    excludes = ['is_active', 'is_staff', 'is_superuser','date_joined' ,'last_login' , 'username']
    authorization= Authorization()
    always_return_data = True
    
  def dehydrate(self , bundle):

		
	setting = Settings.objects.filter(user_id = bundle.obj )
	bundle.data['img'] =	setting[0].img
	del bundle.data["password"]
#	bundle.data['rol'] = setting[0].rol
	return bundle

  def obj_create(self, bundle, request=None, **kwargs):

	error_message = ''

	try:
		bundle = self.full_hydrate(bundle)
		email = bundle.data.get('email')
		check_if_exist = User.objects.filter(email=email)

		if check_if_exist:
			raise BadRequest()
	except:
		
		error_message = 'El email ya existe'
	else:
		
		rol_get = 0 #bundle.data.get("rol")
		bundle.obj.set_password(bundle.data.get('password'))
		bundle.obj.username = email
		user = bundle.obj.save()
		id_new_user =  bundle.obj.id

		new_user_created = bundle.obj
		current_user = bundle.request.user


		AdminCreatedUsers.objects.create( admin = current_user , user = new_user_created )

		data = Settings.objects.create( user_id =  id_new_user , rol = rol_get , users_created = 0 ) 

	finally:

		if error_message:
			raise BadRequest(error_message)
	return bundle



