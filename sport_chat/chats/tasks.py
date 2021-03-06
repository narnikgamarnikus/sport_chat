import ujson as json
from .models import Event, Notification, Message, Team
from celery import shared_task
#from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from annoying.functions import get_object_or_None
from channels import Group
from .signals import create_message



@shared_task
def schedule_notification(notification_pk):
	notification = get_object_or_None(Notification, pk=notification_pk)
	print(notification.event.status)
	if notification and notification.event.status is not 'end':
		print('send_notification')
		send_notification.apply_async(args=(notification_pk, ), countdown=int(notification.every)*60)
		print(int(notification.every)*60)



@shared_task
def send_notification(notification_pk):
	notification = get_object_or_None(Notification, pk=notification_pk)
	event = get_object_or_None(Event, pk=notification.event.pk)

	if notification and event:
		print('yes')

		message = notification.message

		Group('chat-%s' % event.team_left.pk).send({
			"text": json.dumps({
				"notification_message": notification.message
			}),
		}, immediately=True)

		Group('chat-%s' % event.team_right.pk).send({
			"text": json.dumps({
				"notification_message": notification.message
			}),
		}, immediately=True)
		print('seeeeend')
		schedule_notification.apply_async(args=(notification_pk, ))

	'''
	if event:
		if event.status == 'end':
			task = get_object_or_None(
				PeriodicTask, 
				name='sending event notification #{} to event #{}'.format(
					notification_pk,
					event_pk
					)
				)
			task.delete()
		else:
			pass
			#send_notification
	'''

@shared_task
def change_status(event_pk):
	
	event = get_object_or_None(Event, pk=event_pk)
	if event:
		
		if event.status == 'soon':
			event.status = 'online'
		
		elif event.status == 'online':
			event.status = 'end'

		event.save()


@receiver(post_save, sender=Event)
def change_event_status(sender, instance, created, **kwargs):
	
	if created:
		if instance.status == 'soon':
			countdown = instance.start_date - instance.created
		elif instance.status == 'online':
			countdown = instance.end_date - instance.start_date

		change_status.apply_async(args=(instance.pk, ), countdown=countdown.seconds)


@receiver(post_save, sender=Notification)
def schedule_task(sender, instance, created, **kwargs):
	if created:
		print('created')
		schedule_notification(instance.pk)
		print('send notification')
		'''
		every = instance.every

		schedule, created = IntervalSchedule.objects.get_or_create(
			every=every,
			period=IntervalSchedule.MINUTES,
			)

		PeriodicTask.objects.create(
			interval=schedule,
			name='sending event notification #{} to event #{}'.format(
				instance.pk, 
				instance.event.pk
				),
			task='chats.tasks.send_notification',
				args=json.dumps([
					instance.pk,
					instance.event.pk,
					instance.mesage
					]),
				kwargs=json.dumps({
					'be_careful': True,
					}),
				expires=None,
				)
		'''
@shared_task
def create_message_task(**kwargs):
	print('KWARGS IS: ' + str(kwargs))
	
	message = None

	if kwargs['msg_type'] == 4:
		message = '{} joined the room'.format(kwargs['user'].username)
	elif kwargs['msg_type'] == 5:
		message = '{} left the room'.format(kwargs['user'].username)		
	
	if not message:
		message = kwargs['message']
	
	event = get_object_or_None(Event, pk=kwargs['event'])
		
	team = get_object_or_None(Team, pk=kwargs['team'])

	if event and team:
		event_message = Message.objects.create(
			user = kwargs['user'], event = event, team_type = kwargs['team_type'], 
			message = message, msg_type = kwargs['msg_type'], team = team 
		)

@receiver(create_message, sender=Event)
def receiver_create_message(sender, *args, **kwargs):
	print('message was received')
	create_message_task.apply_async(kwargs=kwargs)