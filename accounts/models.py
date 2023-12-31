from django.db import models
#Herramientas 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class MyAccountManager(BaseUserManager):
    
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('el usuario debe tener un email')
        
        if not username:
            raise ValueError('el usuario debe tener un username')
        
        user = self.model(
            
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, first_name, last_name, email, username, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,

        )
        user.is_admin=True
        user.is_active=True
        user.is_staff = True
        user.is_superuser= True    
        user.save(using=self._db)
        return user





class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)


    #campos de atributos de Django
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active =models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

    objects = MyAccountManager()

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email
    
    
    def has_perm(self, perm, obj=None):
        return True
    

    def has_module_perms(self, add_label):
        return True
    
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=50, blank=True)
    address_line2 = models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)

    def __str__(self) -> str:
        return self.user.first_name
    

    def full_address(self):
        return  f"{self.address_line1} {self.address_line2}"
    


