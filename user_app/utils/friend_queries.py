from user_app.models import User

def get_users_by_section(user: User, section):
    # Запити
    if section == 'requests':
        return User.objects.filter(sent_friendships__to_user = user, sent_friendships__status = 'pending').order_by('id')
    # Всі друзі
    if section == 'friends':
        # flat = True [1, 2, 3], без True [(1,), (2,), (3,)]
        sent_friend_ids = list(user.sent_friendships.filter(status= 'accepted').values_list('to_user_id', flat= True))
        received_friend_ids = list(user.received_friendships.filter(status= 'accepted').values_list('from_user_id', flat= True))
        
        return User.objects.filter(id__in= sent_friend_ids + received_friend_ids).order_by('id')
    
    if section == 'recommendations':
        sent_busy_ids = list(user.sent_friendships.values_list("to_user_id", flat= True))
        received_busy_ids = list(user.received_friendships.values_list('from_user_id', flat = True))
        busy_ids = sent_busy_ids + received_busy_ids + [user.id]
        
        return User.objects.exclude(id__in = busy_ids).order_by('id')
        
        
        