# from io import BytesIO
from django import forms
# from django.core.files.base import ContentFile
# from PIL import Image
# 
from .models import Post, Tag, PostLinks, PostImage, PostView
from .utils.compressed_image import _compressed_image

# MAX_COMPRESSED_IMAGE_SIZE = 5 * 1024 * 1024 # 5 Mb

class MultipleFileInput(forms.ClearableFileInput):
    # За замовчуванням можна вибрати тільки один файл, але 
    # властивість allow_multiple_selected задає можливість вибору декількох файлів
    allow_multiple_selected = True
    
class MultipleFileField(forms.FileField):
    '''
        Відповідає за очистку та валідацію отриманих файлів
    '''
    def clean(self, data, initial = None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(data= file, initial= initial) for file in data]
        return single_file_clean(data= data, initial= initial)
    
class PostForm(forms.ModelForm):
    # 
    tags = forms.ModelMultipleChoiceField(
        required = False,
        queryset= Tag.objects.all(),
        widget = forms.CheckboxSelectMultiple
    )
    # 
    images = MultipleFileField(
        required = False,
        widget= MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'})
    )
    
    class Meta:
        model = Post
        fields = ('title', 'topic', 'content')
        labels = {
            'title': 'Назва публікації',
            'topic': 'Тема публікації'
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Природа, книга і спокій 🌿'}),
            'topic': forms.TextInput(attrs={'placeholder': 'Напишіть тему публікаціїї'}),
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Текс посту'})
        }
        
    def __init__(self, *args, links= None, images= None, **kwargs):
        '''
            ініціалізує форму
            
            Параметри Links і images отримуємо не із форми ModelForm, a з view
        '''
        super().__init__(*args, **kwargs)
        
        self.fields['tags'].queryset = Tag.objects.all()
        
        self.links_list = []
        
        self.images_list = []
        
        if links:
            for link in links:
                clean_link = link.strip()
                
                if clean_link:
                    self.links_list.append(clean_link)
                
        if images:
            self.images_list = list(images)
            
    def clean(self):
        cleaned_data = super().clean()
        
        url_field =  forms.URLField()
        image_field = forms.ImageField()
        
        for link in self.links_list:
            try:
                url_field.clean(link)
            except forms.ValidationError:
                self.add_error('links', f"Некоректне посилання: {link}")
        
        for image in self.images_list:
            try:
                image_field.clean(image)
            except forms.ValidationError:
                self.add_error('images', f"Завантажте коректне зображення")
        
        return cleaned_data
    
    def save(self, author, commit= True):
        post: Post = super().save(commit= False)
        post.author = author
        
        if commit:
            post.save()
            
            post.tags.set(self.cleaned_data['tags'])
            
            for url in self.links_list:
                PostLinks.objects.create(post= post, url= url)
            for image in self.images_list:
                PostImage.objects.create(
                    post= post,
                    original_image= image,
                    compressed_image= _compressed_image(image)
                )
                
        return post
    
    # def _compressed_image(self, image):
    #     '''
    #         повна робота з модулем Pillow
    #     '''
        
    #     image.seek(0)
    #     compressed_image = Image.open(image)
    #     compressed_image = compressed_image.convert("RGB")
        
    #     quality = 85
    #     width, height = compressed_image.size
        
    #     while True:
    #         buffer = BytesIO()
    #         compressed_image.save(fp= buffer, format= 'JPEG', quality= quality, optimize= True)
            
    #         if buffer.tell() <= MAX_COMPRESSED_IMAGE_SIZE:
    #             break
            
    #         if quality > 35:
    #             quality -= 10
    #         else:
    #             if width <= 1 or height <= 1:
    #                 break
    #             # Якщо якість вже низька, зменшуємо зображення на 10%
    #             width = int(width * 0.9)
    #             height = int(height * 0.9)
    #             compressed_image = compressed_image.resize((width, height), Image.Resampling.LANCZOS)
                
    #     image.seek(0)
        
    #     compressed_name = f'compressed_{image.name.rsplit('.', 1)[0]}.jpg'
        
    #     return ContentFile(buffer.getvalue(), name= compressed_name)
        
                
                