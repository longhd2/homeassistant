# -*- coding: utf-8 -*-
"""
Lịch âm Việt Nam cho Home Assistant.
- Thuật toán âm lịch: Hồ Ngọc Đức / Jean Meeus
- Múi giờ mặc định: GMT+7
- Sửa lỗi bản cũ: giờ Hoàng đạo/Hắc đạo được tính theo CHI CỦA NGÀY,
  trả về đủ 6 giờ tốt và 6 giờ xấu, không dựa vào lunarDay // 2.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import math
from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv

CONF_DELIMITER = "delimiter"
CONF_TIME_ZONE = "time_zone"

DEFAULT_DELIMITER = "/"
DEFAULT_TIME_ZONE = 7.0

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_DELIMITER, default=DEFAULT_DELIMITER): cv.string,
        vol.Optional(CONF_TIME_ZONE, default=DEFAULT_TIME_ZONE): vol.Coerce(float),
        vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(minutes=5)): cv.time_period,
    }
)

THANG_AM_TEXT = [
    "tháng Giêng", "tháng Hai", "tháng Ba", "tháng Tư",
    "tháng Năm", "tháng Sáu", "tháng Bảy", "tháng Tám",
    "tháng Chín", "tháng Mười", "tháng Mười một", "tháng Chạp",
]

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

GIO = [
    ("Tý", "23h-01h"),
    ("Sửu", "01h-03h"),
    ("Dần", "03h-05h"),
    ("Mão", "05h-07h"),
    ("Thìn", "07h-09h"),
    ("Tỵ", "09h-11h"),
    ("Ngọ", "11h-13h"),
    ("Mùi", "13h-15h"),
    ("Thân", "15h-17h"),
    ("Dậu", "17h-19h"),
    ("Tuất", "19h-21h"),
    ("Hợi", "21h-23h"),
]

# Mẫu giờ Hoàng đạo theo 6 nhóm Chi ngày.
# Đây là cách dùng phổ biến trong mã lịch âm Hồ Ngọc Đức.
GIO_HD_PATTERNS = [
    "110100101100",  # Tý / Ngọ
    "001101001011",  # Sửu / Mùi
    "110011010010",  # Dần / Thân
    "101100110100",  # Mão / Dậu
    "001011001101",  # Thìn / Tuất
    "010010110011",  # Tỵ / Hợi
]


def jd_from_date(dd: int, mm: int, yy: int) -> int:
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def jd_to_date(jd: int) -> tuple[int, int, int]:
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082

    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


def new_moon(k: int) -> float:
    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    dr = math.pi / 180.0

    jd1 = (
        2415020.75933
        + 29.53058868 * k
        + 0.0001178 * t2
        - 0.000000155 * t3
    )
    jd1 += 0.00033 * math.sin((166.56 + 132.87 * t - 0.009173 * t2) * dr)

    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
    mpr = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3

    c1 = (0.1734 - 0.000393 * t) * math.sin(m * dr) + 0.0021 * math.sin(2 * m * dr)
    c1 -= 0.4068 * math.sin(mpr * dr)
    c1 += 0.0161 * math.sin(2 * mpr * dr)
    c1 -= 0.0004 * math.sin(3 * mpr * dr)
    c1 += 0.0104 * math.sin(2 * f * dr)
    c1 -= 0.0051 * math.sin((m + mpr) * dr)
    c1 -= 0.0074 * math.sin((m - mpr) * dr)
    c1 += 0.0004 * math.sin((2 * f + m) * dr)
    c1 -= 0.0004 * math.sin((2 * f - m) * dr)
    c1 -= 0.0006 * math.sin((2 * f + mpr) * dr)
    c1 += 0.0010 * math.sin((2 * f - mpr) * dr)
    c1 += 0.0005 * math.sin((2 * mpr + m) * dr)

    if t < -11:
        delta_t = (
            0.001
            + 0.000839 * t
            + 0.0002261 * t2
            - 0.00000845 * t3
            - 0.000000081 * t * t3
        )
    else:
        delta_t = -0.000278 + 0.000265 * t + 0.000262 * t2

    return jd1 + c1 - delta_t


def sun_longitude(jdn: float) -> float:
    t = (jdn - 2451545.0) / 36525.0
    t2 = t * t
    dr = math.pi / 180.0

    m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t * t2
    l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2

    dl = (1.914600 - 0.004817 * t - 0.000014 * t2) * math.sin(dr * m)
    dl += (0.019993 - 0.000101 * t) * math.sin(2 * dr * m)
    dl += 0.000290 * math.sin(3 * dr * m)

    l = (l0 + dl) * dr
    return l - 2 * math.pi * int(l / (2 * math.pi))


def get_sun_longitude(day_number: int, time_zone: float) -> int:
    return int(sun_longitude(day_number - 0.5 - time_zone / 24.0) / math.pi * 6)


def get_new_moon_day(k: int, time_zone: float) -> int:
    return int(new_moon(k) + 0.5 + time_zone / 24.0)


def get_lunar_month_11(yy: int, time_zone: float) -> int:
    off = jd_from_date(31, 12, yy) - 2415021
    k = int(off / 29.530588853)
    nm = get_new_moon_day(k, time_zone)
    sun_long = get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = get_new_moon_day(k - 1, time_zone)
    return nm


def get_leap_month_offset(a11: int, time_zone: float) -> int:
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = -1
    i = 1
    arc = get_sun_longitude(get_new_moon_day(k + i, time_zone), time_zone)

    while True:
        last = arc
        i += 1
        arc = get_sun_longitude(get_new_moon_day(k + i, time_zone), time_zone)
        if arc == last or i >= 14:
            break

    return i - 1


def solar_to_lunar(dd: int, mm: int, yy: int, time_zone: float = 7.0) -> tuple[int, int, int, int]:
    day_number = jd_from_date(dd, mm, yy)
    k = int((day_number - 2415021.076998695) / 29.530588853)

    month_start = get_new_moon_day(k + 1, time_zone)
    if month_start > day_number:
        month_start = get_new_moon_day(k, time_zone)

    a11 = get_lunar_month_11(yy, time_zone)
    b11 = a11

    if a11 >= month_start:
        lunar_year = yy
        a11 = get_lunar_month_11(yy - 1, time_zone)
    else:
        lunar_year = yy + 1
        b11 = get_lunar_month_11(yy + 1, time_zone)

    lunar_day = day_number - month_start + 1
    diff = int((month_start - a11) / 29)
    lunar_leap = 0
    lunar_month = diff + 11

    if b11 - a11 > 365:
        leap_month_diff = get_leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = 1

    if lunar_month > 12:
        lunar_month -= 12

    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1

    return lunar_day, lunar_month, lunar_year, lunar_leap


def can_chi_ngay(dd: int, mm: int, yy: int) -> str:
    jd = jd_from_date(dd, mm, yy)
    return f"{CAN[(jd + 9) % 10]} {CHI[(jd + 1) % 12]}"


def can_chi_nam(lunar_year: int) -> str:
    return f"{CAN[(lunar_year + 6) % 10]} {CHI[(lunar_year + 8) % 12]}"


def gio_hoang_dao_hac_dao(dd: int, mm: int, yy: int) -> tuple[list[str], list[str]]:
    jd = jd_from_date(dd, mm, yy)
    chi_ngay_idx = (jd + 1) % 12
    pattern = GIO_HD_PATTERNS[chi_ngay_idx % 6]

    good: list[str] = []
    bad: list[str] = []

    for i, (ten, khung) in enumerate(GIO):
        text = f"{ten} ({khung})"
        if pattern[i] == "1":
            good.append(text)
        else:
            bad.append(text)

    return good, bad


def lunar_day_text(day: int) -> str:
    if day == 1:
        return "mùng 1"
    if day < 10:
        return f"mùng {day}"
    if day == 10:
        return "mùng 10"
    if day == 15:
        return "15, ngày rằm"
    return str(day)


@dataclass(frozen=True)
class LunarInfo:
    solar_date: date
    lunar_day: int
    lunar_month: int
    lunar_year: int
    lunar_leap: int
    good_hours: list[str]
    bad_hours: list[str]

    @property
    def lunar_numeric(self) -> str:
        suffix = " nhuận" if self.lunar_leap else ""
        return f"{self.lunar_day}/{self.lunar_month}/{self.lunar_year}{suffix}"

    @property
    def lunar_text(self) -> str:
        month_text = THANG_AM_TEXT[self.lunar_month - 1]
        leap_text = " nhuận" if self.lunar_leap else ""
        return (
            f"{lunar_day_text(self.lunar_day)} {month_text}{leap_text}, "
            f"năm {can_chi_nam(self.lunar_year)}"
        )

    @property
    def day_can_chi(self) -> str:
        d = self.solar_date
        return can_chi_ngay(d.day, d.month, d.year)
