# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime

class MeetingRoomBooking(Document):
	def validate(self):
		self.validate_time_slots()
		self.check_room_availability()
		self.validate_room_capacity()
		self.validate_room_facilities()
	
	def validate_time_slots(self):
		"""Validate that end time is after start time"""
		if self.start_time and self.end_time:
			start_datetime = get_datetime(f"{self.booking_date} {self.start_time}")
			end_datetime = get_datetime(f"{self.booking_date} {self.end_time}")
			
			if end_datetime <= start_datetime:
				frappe.throw(_("End time must be after start time"))
			
			# Check if booking is in the past
			if start_datetime < now_datetime() and self.is_new():
				frappe.throw(_("Cannot book a meeting room in the past"))
	
	def check_room_availability(self):
		"""Check if the room is available for the requested time slot"""
		if not self.meeting_room or not self.booking_date or not self.start_time or not self.end_time:
			return
		
		# Check if room is active
		room = frappe.get_doc("Meeting Room", self.meeting_room)
		if not room.is_active:
			frappe.throw(_("Meeting Room {0} is not active").format(self.meeting_room))
		
		# Check for overlapping bookings
		overlapping_bookings = frappe.db.sql("""
			SELECT name, meeting_title, start_time, end_time
			FROM `tabMeeting Room Booking`
			WHERE meeting_room = %(room)s
				AND booking_date = %(date)s
				AND name != %(current_booking)s
				AND status NOT IN ('Rejected', 'Cancelled')
				AND docstatus < 2
				AND (
					(start_time < %(end_time)s AND end_time > %(start_time)s)
				)
		""", {
			'room': self.meeting_room,
			'date': self.booking_date,
			'start_time': self.start_time,
			'end_time': self.end_time,
			'current_booking': self.name or 'new'
		}, as_dict=True)
		
		if overlapping_bookings:
			conflict_details = "<br>".join([
				f"• {b.meeting_title} ({b.start_time} - {b.end_time})"
				for b in overlapping_bookings
			])
			frappe.throw(
				_("Meeting Room {0} is already booked for the selected time slot.<br><br>Conflicting bookings:<br>{1}")
				.format(self.meeting_room, conflict_details),
				title=_("Room Not Available")
			)
	
	def validate_room_capacity(self):
		"""Validate that the number of attendees doesn't exceed room capacity"""
		if self.number_of_attendees and self.meeting_room:
			room = frappe.get_doc("Meeting Room", self.meeting_room)
			if self.number_of_attendees > room.capacity:
				frappe.msgprint(
					_("Number of attendees ({0}) exceeds room capacity ({1})")
					.format(self.number_of_attendees, room.capacity),
					indicator='orange',
					alert=True
				)
	
	def validate_room_facilities(self):
		"""Check if required facilities are available in the room"""
		if not self.meeting_room:
			return
		
		room = frappe.get_doc("Meeting Room", self.meeting_room)
		warnings = []
		
		if self.requires_projector and not room.has_projector:
			warnings.append(_("Projector"))
		
		if self.requires_video_conferencing and not room.has_video_conferencing:
			warnings.append(_("Video Conferencing"))
		
		if warnings:
			frappe.msgprint(
				_("The selected room does not have the following required facilities: {0}")
				.format(", ".join(warnings)),
				indicator='orange',
				alert=True
			)
	
	def on_submit(self):
		"""Auto-approve if user has permission, otherwise set to pending"""
		if self.status == "Pending":
			if frappe.has_permission("Meeting Room Booking", "approve"):
				self.db_set("status", "Approved")
				self.db_set("approved_by", frappe.session.user)
				self.db_set("approval_date", now_datetime())
	
	def on_cancel(self):
		"""Set status to cancelled on cancel"""
		self.db_set("status", "Cancelled")

@frappe.whitelist()
def check_room_availability(room, date, start_time, end_time, current_booking=None):
	"""Check if a meeting room is available for the given time slot"""
	
	overlapping_bookings = frappe.db.sql("""
		SELECT name, meeting_title, start_time, end_time, booked_by
		FROM `tabMeeting Room Booking`
		WHERE meeting_room = %(room)s
			AND booking_date = %(date)s
			AND name != %(current_booking)s
			AND status NOT IN ('Rejected', 'Cancelled')
			AND docstatus < 2
			AND (
				(start_time < %(end_time)s AND end_time > %(start_time)s)
			)
	""", {
		'room': room,
		'date': date,
		'start_time': start_time,
		'end_time': end_time,
		'current_booking': current_booking or 'new'
	}, as_dict=True)
	
	return {
		'available': len(overlapping_bookings) == 0,
		'conflicts': overlapping_bookings
	}

@frappe.whitelist()
def get_room_schedule(room, date):
	"""Get all bookings for a room on a specific date"""
	
	bookings = frappe.db.sql("""
		SELECT name, meeting_title, start_time, end_time, status, booked_by
		FROM `tabMeeting Room Booking`
		WHERE meeting_room = %(room)s
			AND booking_date = %(date)s
			AND status NOT IN ('Rejected', 'Cancelled')
			AND docstatus < 2
		ORDER BY start_time
	""", {
		'room': room,
		'date': date
	}, as_dict=True)
	
	return bookings
