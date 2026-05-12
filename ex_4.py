import re
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from dateutil.rrule import rrulestr
from dateutil.tz import gettz

# ------------------------ Класс "Занятие" ------------------------
class Lesson:
    def __init__(self, start: datetime, end: datetime, subject: str,
                 teacher: str, room: str, lesson_type: str, group: str = ""):
        # Приводим всё к UTC для единообразия
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
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[self.start.weekday()]

    def __repr__(self) -> str:
        return (f"Lesson({self.start.strftime('%Y-%m-%d %H:%M UTC')} "
                f"{self.subject} [{self.lesson_type}], {self.teacher}, {self.room})")


# ------------------------ Класс "Расписание" ------------------------
class Schedule:
    def __init__(self):
        self.lessons: List[Lesson] = []

    def load_from_ics(self, filename: str, target_group: str = "") -> None:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл {filename} не найден.")

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

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

            teacher_match = re.search(r'Преподаватель:\s*(.*?)(?:\n|$)', description)
            teacher = teacher_match.group(1).strip() if teacher_match else ""

            # Извлечение типа занятия из SUMMARY (например, "(лекция)")
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

            # Если есть RRULE — генерируем серию
            if rrule_line:
                # Создаём правило, явно передавая dtstart с таймзоной
                rule_str = f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\nRRULE:{rrule_line}"
                try:
                    rrule = rrulestr(rule_str, dtstart=dtstart, ignoretz=False)
                    occurrences = list(rrule)
                    duration = dtend - dtstart
                    for occ_start in occurrences:
                        occ_end = occ_start + duration
                        lesson = Lesson(occ_start, occ_end, subject, teacher, location, lesson_type, target_group)
                        self.lessons.append(lesson)
                except Exception as e:
                    print(f"Ошибка RRULE для {subject}: {e}")
            else:
                lesson = Lesson(dtstart, dtend, subject, teacher, location, lesson_type, target_group)
                self.lessons.append(lesson)

    @staticmethod
    def _extract_field(text: str, field_name: str, full: bool = False) -> Optional[str]:
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
        match = re.search(r'TZID=([^:]+)', line)
        return match.group(1) if match else None

    @staticmethod
    def _parse_datetime(line: str, tzid: Optional[str]) -> Optional[datetime]:
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
        Возвращает занятия, попадающие в неделю (пн–вс), содержащую target_date.
        Границы недели вычисляются в локальной таймзоне target_date.
        """
        # Приводим target_date к осознанной таймзоне, если нужно
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=timezone.utc)
        local_tz = target_date.tzinfo

        # Переводим в локальную таймзону
        local_date = target_date.astimezone(local_tz)
        monday_local = local_date - timedelta(days=local_date.weekday())
        monday_local = monday_local.replace(hour=0, minute=0, second=0, microsecond=0)
        sunday_local = monday_local + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Границы в UTC для сравнения с уроками
        monday_utc = monday_local.astimezone(timezone.utc)
        sunday_utc = sunday_local.astimezone(timezone.utc)

        week_lessons = [l for l in self.lessons if monday_utc <= l.start <= sunday_utc]
        week_lessons.sort(key=lambda l: l.start)
        return week_lessons


# ------------------------ Вспомогательные функции ------------------------
def get_current_week_parity_from_date(semester_start: datetime, target_date: datetime) -> int:
    """Возвращает 1 (числитель) или 2 (знаменатель) для недели, содержащей target_date."""
    if target_date.tzinfo is None:
        target_date = target_date.replace(tzinfo=timezone.utc)
    if semester_start.tzinfo is None:
        semester_start = semester_start.replace(tzinfo=timezone.utc)

    delta_days = (target_date - semester_start).days
    week_number = (delta_days // 7) + 1
    return 1 if (week_number % 2 == 1) else 2


def display_weekly_schedule(schedule: Schedule, target_date: datetime, group_name: str) -> None:
    """Выводит расписание группы на неделю, содержащую target_date."""
    week_lessons = schedule.filter_by_week(target_date)

    if not week_lessons:
        print(f"\nНа неделе {target_date.strftime('%d.%m.%Y')} занятий для группы {group_name} не найдено.")
        return

    # Для вывода преобразуем время в локальное (например, Asia/Novosibirsk)
    local_tz = target_date.tzinfo if target_date.tzinfo else gettz("Asia/Novosibirsk")

    print(f"\n=== Расписание группы {group_name} на неделю {target_date.strftime('%d.%m.%Y')} ===")
    current_day = None
    for lesson in week_lessons:
        local_start = lesson.start.astimezone(local_tz)
        if local_start.strftime("%A") != current_day:
            current_day = local_start.strftime("%A")
            print(f"\n--- {lesson.day_name_russian} ({local_start.strftime('%d.%m')}) ---")
        print(f"{local_start.strftime('%H:%M')}  {lesson.subject} ({lesson.lesson_type})")
        print(f"         Преподаватель: {lesson.teacher or '—'}")
        print(f"         Аудитория: {lesson.room}")


# ------------------------ Демонстрация ------------------------
def main():
    ics_filename = "schedule.ics"
    group = "24816"

    if not os.path.exists(ics_filename):
        print(f"Файл {ics_filename} не найден. Поместите его в текущую папку.")
        return

    # Проверка наличия библиотеки dateutil
    try:
        import dateutil
    except ImportError:
        print("Установите python-dateutil: pip install python-dateutil")
        return

    schedule = Schedule()
    print("Загрузка расписания из ICS...")
    schedule.load_from_ics(ics_filename, target_group=group)

    print(f"Всего загружено занятий: {len(schedule.lessons)}")
    if schedule.lessons:
        print("Пример первых 5 занятий:")
        for i, les in enumerate(schedule.lessons[:5], 1):
            print(f"{i}. {les}")

    # Начало семестра – 2 сентября 2024 (понедельник)
    semester_start = datetime(2024, 9, 2, tzinfo=gettz("Asia/Novosibirsk"))
    # Текущая дата (можно заменить на любую для теста)
    today = datetime.now().astimezone(gettz("Asia/Novosibirsk"))
    # Для ручной проверки, например:
    # today = datetime(2024, 9, 9, tzinfo=gettz("Asia/Novosibirsk"))

    display_weekly_schedule(schedule, today, group)

    parity = get_current_week_parity_from_date(semester_start, today)
    print(f"\nЧётность текущей недели: {'числитель' if parity == 1 else 'знаменатель'}.")


if __name__ == "__main__":
    main()