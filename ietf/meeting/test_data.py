import datetime

from ietf.doc.models import Document, State
from ietf.group.models import Group
from ietf.meeting.models import (Meeting, Room, TimeSlot, Session, Schedule, SchedTimeSessAssignment,
    ResourceAssociation, SessionPresentation, UrlResource)
from ietf.meeting.helpers import create_interim_meeting
from ietf.name.models import RoomResourceName
from ietf.person.models import Person
from ietf.utils.test_data import make_test_data

def make_interim_meeting(group,date,status='sched'):
    system_person = Person.objects.get(name="(System)")
    time = datetime.datetime.combine(date, datetime.time(9))
    meeting = create_interim_meeting(group=group,date=date)
    session = Session.objects.create(meeting=meeting, group=group,
        attendees=10, requested_by=system_person,
        requested_duration=20, status_id=status,
        remote_instructions='http://webex.com',
        scheduled=datetime.datetime.now(),type_id="session")
    slot = TimeSlot.objects.create(
        meeting=meeting,
        type_id="session",
        duration=session.requested_duration,
        time=time)
    SchedTimeSessAssignment.objects.create(
        timeslot=slot,
        session=session,
        schedule=session.meeting.agenda)
    return meeting

def make_meeting_test_data(meeting=None):
    if not Group.objects.filter(acronym='mars'):
        make_test_data()
    system_person = Person.objects.get(name="(System)")
    plainman = Person.objects.get(user__username="plain")
    #secretary = Person.objects.get(user__username="secretary") ## not used

    if not meeting:
        meeting = Meeting.objects.get(number="42", type="ietf")
    schedule = Schedule.objects.create(meeting=meeting, owner=plainman, name="test-agenda", visible=True, public=True)
    unofficial_schedule = Schedule.objects.create(meeting=meeting, owner=plainman, name="test-unofficial-agenda", visible=True, public=True)

    # test room
    pname = RoomResourceName.objects.create(name='projector',slug='proj')
    projector = ResourceAssociation.objects.create(name=pname,icon="notfound.png",desc="Basic projector")
    room = Room.objects.create(meeting=meeting, name="Test Room", capacity=123, functional_name="Testing Ground")
    room.session_types.add("session")
    room.resources.add(projector)
    asname = RoomResourceName.objects.create(name='Audio Stream', slug='audiostream')
    UrlResource.objects.create(name=asname, room=room, url='http://ietf{number}streaming.dnsalias.net/ietf/ietf{number}1.m3u'.format(number=meeting.number))

    # another room
    breakfast_room = Room.objects.create(meeting=meeting, name="Breakfast Room", capacity=40)
    breakfast_room.session_types.add("lead")

    # slots
    slot1 = TimeSlot.objects.create(meeting=meeting, type_id="session", duration=30 * 60, location=room,
                                    time=datetime.datetime.combine(datetime.date.today(), datetime.time(9, 30)))
    slot2 = TimeSlot.objects.create(meeting=meeting, type_id="session", duration=30 * 60, location=room,
                                    time=datetime.datetime.combine(datetime.date.today(), datetime.time(10, 30)))
    breakfast_slot = TimeSlot.objects.create(meeting=meeting, type_id="lead", duration=90 * 60,
                                   location=breakfast_room, 
                                   time=datetime.datetime.combine(datetime.date.today(),datetime.time(7,0)))
    # mars WG
    mars = Group.objects.get(acronym='mars')
    mars_session = Session.objects.create(meeting=meeting, group=mars,
                                          attendees=10, requested_by=system_person,
                                          requested_duration=20, status_id="schedw",
                                          scheduled=datetime.datetime.now(),type_id="session")
    SchedTimeSessAssignment.objects.create(timeslot=slot1, session=mars_session, schedule=schedule)
    SchedTimeSessAssignment.objects.create(timeslot=slot2, session=mars_session, schedule=unofficial_schedule)

    # ames WG
    ames_session = Session.objects.create(meeting=meeting, group=Group.objects.get(acronym="ames"),
                                          attendees=10, requested_by=system_person,
                                          requested_duration=20, status_id="schedw",
                                          scheduled=datetime.datetime.now(),type_id="session")
    SchedTimeSessAssignment.objects.create(timeslot=slot2, session=ames_session, schedule=schedule)
    SchedTimeSessAssignment.objects.create(timeslot=slot1, session=ames_session, schedule=unofficial_schedule)

    # IESG breakfast
    iesg_session = Session.objects.create(meeting=meeting, group=Group.objects.get(acronym="iesg"),
                                          name="IESG Breakfast",
                                          attendees=25, requested_by=system_person,
                                          requested_duration=20, status_id="schedw",
                                          scheduled=datetime.datetime.now(),type_id="lead")
    SchedTimeSessAssignment.objects.create(timeslot=breakfast_slot, session=iesg_session, schedule=schedule)
    # No breakfast on unofficial schedule

    meeting.agenda = schedule
    meeting.save()

    # Convenience for the tests
    meeting.unofficial_schedule = unofficial_schedule
    

    doc = Document.objects.create(name='agenda-mars-ietf-42', type_id='agenda', title="Agenda", external_url="agenda-mars.txt",group=mars,rev='00')
    doc.set_state(State.objects.get(type=doc.type_id, slug="active"))
    mars_session.sessionpresentation_set.add(SessionPresentation(session=mars_session,document=doc,rev=doc.rev))

    doc = Document.objects.create(name='minutes-mars-ietf-42', type_id='minutes', title="Minutes", external_url="minutes-mars.txt",group=mars,rev='00')
    doc.set_state(State.objects.get(type=doc.type_id, slug="active"))
    mars_session.sessionpresentation_set.add(SessionPresentation(session=mars_session,document=doc,rev=doc.rev))

    doc = Document.objects.create(name='slides-mars-ietf-42', type_id='slides', title="Slideshow", external_url="slides-mars.txt",group=mars,rev='00')
    doc.set_state(State.objects.get(type=doc.type_id, slug="active"))
    doc.set_state(State.objects.get(type='reuse_policy',slug='single'))
    mars_session.sessionpresentation_set.add(SessionPresentation(session=mars_session,document=doc,rev=doc.rev))

    doc = Document.objects.create(name='slides-mars-ietf-42-deleted', type_id='slides', title="Bad Slideshow", external_url="slides-mars-deleted.txt",group=mars,rev='00')
    doc.set_state(State.objects.get(type=doc.type_id, slug="deleted"))
    doc.set_state(State.objects.get(type='reuse_policy',slug='single'))
    mars_session.sessionpresentation_set.add(SessionPresentation(session=mars_session,document=doc,rev=doc.rev))
    
    # Future Interim Meetings
    date = datetime.date.today() + datetime.timedelta(days=365)
    date2 = datetime.date.today() + datetime.timedelta(days=1000)
    ames = Group.objects.get(acronym="ames")

    make_interim_meeting(group=mars,date=date,status='sched')
    make_interim_meeting(group=mars,date=date2,status='apprw')
    make_interim_meeting(group=ames,date=date,status='canceled')
    make_interim_meeting(group=ames,date=date2,status='apprw')

    return meeting



