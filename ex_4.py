"""
Module for parsing and displaying weekly schedules from an ICS file.

Provides classes Lesson (single event) and Schedule (collection of lessons),
with filtering by week and group, plus UTC normalisation and timezone handling.
"""

import re
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from dateutil.rrule import rrulestr
from dateutil.tz import gettz


# ------------------------ Lesson class ------------------------
class Lesson:
    """A single lesson (event) with start/end times and metadata."""

    def __init__(self, start: datetime, end: datetime, subject: str,
                 teacher: str, room: str, lesson_type: str, group: str = "") -> None:
        """
        Initialise a lesson.

        All datetime objects are normalised to UTC for consistent handling.

        Args:
            start: Start datetime (may be naive or timezone‑aware).
            end: End datetime.
            subject: Lesson subject/title.
            teacher: Teacher's name.
            room: Room number or name.
            lesson_type: e.g. "лекция", "практика".
            group: Group identifier (optional).
        """
        # Convert to UTC for uniform storage
        if start.tzinfo:
            self.start = start.astimezone(timezone.utc)
        else:
            self.start = start.replace(tzinfo=timezone.utc)

        if end.tzinfo:
            self.end = end.astimezone(timezone.utc)
        else:
            self.end = end.replace(tzinfo=timezone.utc)

        self.subject = subject
        self.teacher = teacher
        self.room = room
        self.lesson_type = lesson_type
        self.group = group

    @property
    def day_name_russian(self) -> str:
        """Return the day of week in Russian (Monday–Sunday)."""
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[self.start.weekday()]

    def __repr__(self) -> str:
        """Developer‑friendly representation."""
        return (f"Lesson({self.start.strftime('%Y-%m-%d %H:%M UTC')} "
                f"{self.subject} [{self.lesson_type}], {self.teacher}, {self.room})")


# ------------------------ Schedule class ------------------------
class Schedule:
    """Collection of lessons, with ICS loading and filtering capabilities."""

    def __init__(self) -> None:
        """Initialise an empty schedule."""
        self.lessons: List[Lesson] = []

    def load_from_ics(self, filename: str, target_group: str = "") -> None:
        """
        Parse an ICS file and append lessons to the schedule.

        Args:
            filename: Path to the ICS file.
            target_group: If provided, only lessons whose URL contains this group
                          are loaded (for multi‑group ICS files).

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} not found.")

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into VEVENT blocks
        event_blocks = re.split(r'\n(?=BEGIN:VEVENT)', content, flags=re.IGNORECASE)

        for block in event_blocks:
            if not block.strip().startswith('BEGIN:VEVENT'):
                continue

            summary = self._extract_field(block, 'SUMMARY')
            if not summary:
                continue

            url = self._extract_field(block, 'URL')
            if target_group and (not url or target_group not in url):
                continue

            location = self._extract_field(block, 'LOCATION') or "не указана"
            description = self._extract_field(block, 'DESCRIPTION') or ""

            # Extract teacher from description
            teacher_match = re.search(r'Преподаватель:\s*(.*?)(?:\n|$)', description)
            teacher = teacher_match.group(1).strip() if teacher_match else ""

            # Extract lesson type from SUMMARY, e.g. "(лекция)"
            lesson_type = ""
            match_type = re.search(r'\((.*?)\)$', summary)
            if match_type:
                lesson_type = match_type.group(1)
                subject = summary[:match_type.start()].strip()
            else:
                subject = summary

            dtstart_line = self._extract_field(block, 'DTSTART', full=True)
            dtend_line = self._extract_field(block, 'DTEND', full=True)
            rrule_line = self._extract_field(block, 'RRULE')

            if not dtstart_line or not dtend_line:
                continue

            tz = self._extract_tzid(dtstart_line)
            dtstart = self._parse_datetime(dtstart_line, tz)
            dtend = self._parse_datetime(dtend_line, tz)
            if not dtstart or not dtend:
                continue

            # Handle recurring events (RRULE)
            if rrule_line:
                rule_str = f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\nRRULE:{rrule_line}"
                try:
                    rrule = rrulestr(rule_str, dtstart=dtstart, ignoretz=False)
                    occurrences = list(rrule)
                    duration = dtend - dtstart
                    for occ_start in occurrences:
                        occ_end = occ_start + duration
                        lesson = Lesson(occ_start, occ_end, subject, teacher,
                                        location, lesson_type, target_group)
                        self.lessons.append(lesson)
                except Exception as e:
                    print(f"RRULE error for {subject}: {e}")
            else:
                # Single event
                lesson = Lesson(dtstart, dtend, subject, teacher, location,
                                lesson_type, target_group)
                self.lessons.append(lesson)

    @staticmethod
    def _extract_field(text: str, field_name: str, full: bool = False) -> Optional[str]:
        """
        Extract a field value from a line in an ICS block.

        Args:
            text: The block of ICS text.
            field_name: Field name (e.g. 'SUMMARY').
            full: If True, return the whole line; otherwise only the value after colon.

        Returns:
            Field value (or full line) or None if not found.
        """
        for line in text.splitlines():
            if line.upper().startswith(field_name.upper()):
                if full:
                    return line
                if ':' in line:
                    return line.split(':', 1)[1].strip()
                return ""
        return None

    @staticmethod
    def _extract_tzid(line: str) -> Optional[str]:
        """
        Extract TZID property from a DTSTART/DTEND line.

        Args:
            line: The line containing the datetime property.

        Returns:
            Timezone identifier string, or None.
        """
        match = re.search(r'TZID=([^:]+)', line)
        return match.group(1) if match else None

    @staticmethod
    def _parse_datetime(line: str, tzid: Optional[str]) -> Optional[datetime]:
        """
        Parse a datetime from an ICS property line.

        Args:
            line: The full property line (e.g. "DTSTART;TZID=...:20240902T100000").
            tzid: Optional timezone identifier extracted from the line.

        Returns:
            A datetime object (aware if tzid is provided), or None on failure.
        """
        if ':' not in line:
            return None
        value = line.split(':', 1)[1].strip()
        match = re.match(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})', value)
        if match:
            year, month, day, hour, minute, second = map(int, match.groups())
            dt = datetime(year, month, day, hour, minute, second)
            if tzid:
                tz = gettz(tzid)
                if tz:
                    dt = dt.replace(tzinfo=tz)
            return dt
        return None

    def filter_by_week(self, target_date: datetime) -> List[Lesson]:
        """
        Return lessons that fall within the week containing target_date.

        The week boundaries are Monday 00:00 to Sunday 23:59 in the local timezone
        of target_date. Lessons are compared in UTC.

        Args:
            target_date: Any date within the desired week (timezone‑aware or naive).

        Returns:
            Sorted list of Lesson objects for that week.
        """
        # Ensure target_date is timezone‑aware
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=timezone.utc)
        local_tz = target_date.tzinfo

        # Convert to local timezone to compute Monday 00:00
        local_date = target_date.astimezone(local_tz)
        monday_local = local_date - timedelta(days=local_date.weekday())
        monday_local = monday_local.replace(hour=0, minute=0, second=0, microsecond=0)
        sunday_local = monday_local + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Convert boundaries to UTC for comparison with lesson.start (UTC)
        monday_utc = monday_local.astimezone(timezone.utc)
        sunday_utc = sunday_local.astimezone(timezone.utc)

        week_lessons = [l for l in self.lessons if monday_utc <= l.start <= sunday_utc]
        week_lessons.sort(key=lambda l: l.start)
        return week_lessons


# ------------------------ Helper functions ------------------------
def get_current_week_parity_from_date(semester_start: datetime, target_date: datetime) -> int:
    """
    Determine whether the week containing target_date is the numerator (1) or denominator (2).

    Assumes the semester starts on a Monday. Weeks are counted from 1.
    Odd week numbers -> numerator (1), even week numbers -> denominator (2).

    Args:
        semester_start: Start date of the semester (should be a Monday).
        target_date: The date to check.

    Returns:
        1 for numerator, 2 for denominator.
    """
    if target_date.tzinfo is None:
        target_date = target_date.replace(tzinfo=timezone.utc)
    if semester_start.tzinfo is None:
        semester_start = semester_start.replace(tzinfo=timezone.utc)

    delta_days = (target_date - semester_start).days
    week_number = (delta_days // 7) + 1
    return 1 if (week_number % 2 == 1) else 2


def display_weekly_schedule(schedule: Schedule, target_date: datetime, group_name: str) -> None:
    """
    Print a formatted weekly schedule for a group.

    Args:
        schedule: The Schedule object containing all lessons.
        target_date: Any date inside the desired week.
        group_name: Name of the group (display only).
    """
    week_lessons = schedule.filter_by_week(target_date)

    if not week_lessons:
        print(f"\nNo lessons found for week {target_date.strftime('%d.%m.%Y')} for group {group_name}.")
        return

    # Use the target_date's timezone (or default to Asia/Novosibirsk) for display
    local_tz = target_date.tzinfo if target_date.tzinfo else gettz("Asia/Novosibirsk")

    print(f"\n=== Schedule for group {group_name}, week starting {target_date.strftime('%d.%m.%Y')} ===")
    current_day = None
    for lesson in week_lessons:
        local_start = lesson.start.astimezone(local_tz)
        day_name = local_start.strftime("%A")
        if day_name != current_day:
            current_day = day_name
            print(f"\n--- {lesson.day_name_russian} ({local_start.strftime('%d.%m')}) ---")
        print(f"{local_start.strftime('%H:%M')}  {lesson.subject} ({lesson.lesson_type})")
        print(f"         Teacher: {lesson.teacher or '—'}")
        print(f"         Room: {lesson.room}")


# ------------------------ Demonstration ------------------------
def main() -> None:
    """Main entry point: load schedule, display weekly timetable and week parity."""
    ics_filename = "schedule.ics"
    group = "24816"

    if not os.path.exists(ics_filename):
        print(f"File {ics_filename} not found. Place it in the current folder.")
        return

    # Check for python-dateutil
    try:
        import dateutil  # noqa
    except ImportError:
        print("Install python-dateutil: pip install python-dateutil")
        return

    schedule = Schedule()
    print("Loading schedule from ICS...")
    schedule.load_from_ics(ics_filename, target_group=group)

    print(f"Total lessons loaded: {len(schedule.lessons)}")
    if schedule.lessons:
        print("First 5 lessons:")
        for i, les in enumerate(schedule.lessons[:5], 1):
            print(f"{i}. {les}")

    # Semester start: Monday 2 September 2024, local time (Asia/Novosibirsk)
    semester_start = datetime(2024, 9, 2, tzinfo=gettz("Asia/Novosibirsk"))
    # Current date (can be replaced with any test date)
    today = datetime.now().astimezone(gettz("Asia/Novosibirsk"))
    # Example manual test date:
    # today = datetime(2024, 9, 9, tzinfo=gettz("Asia/Novosibirsk"))

    display_weekly_schedule(schedule, today, group)

    parity = get_current_week_parity_from_date(semester_start, today)
    print(f"\nParity of current week: {'numerator' if parity == 1 else 'denominator'}.")


if __name__ == "__main__":
    main()
