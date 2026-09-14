# ViPi Family Components for Home Assistant

Bộ này tách các chức năng gia đình thành 3 custom integration độc lập, cấu hình bằng giao diện Home Assistant:

- `ViPi TV` (`vipi_tv`): quản lý thời gian xem TV trẻ em.
- `ViPi Alarm` (`vipi_alarm`): báo thức gia đình, có thể đọc lịch âm.
- `ViPi Schedule` (`vipi_schedule`): nhắc lịch học/lịch sinh hoạt.
- `lich_am`: engine lịch âm Việt Nam chạy local.

## 1. Cài đặt

Sao lưu `/config` trước khi làm.

Chép toàn bộ 4 thư mục sau vào:

```text
/config/custom_components/
├── vipi_tv/
├── vipi_alarm/
├── vipi_schedule/
└── lich_am/
```

Khởi động lại Home Assistant.

Sau đó vào:

```text
Settings
→ Devices & services
→ Add integration
```

Tìm và thêm lần lượt:

```text
ViPi TV
ViPi Alarm
ViPi Schedule
```

`lich_am` được khai báo bằng YAML vì đây là engine sensor local. Thêm vào `configuration.yaml`:

```yaml
sensor:
  - platform: lich_am
    delimiter: "/"
    time_zone: 7
    scan_interval: "00:05:00"
```

Khởi động lại HA sau khi thêm.

> Nếu `configuration.yaml` đã có khóa `sensor:` thì gộp dòng `- platform: lich_am` vào khóa đó, không tạo hai khóa `sensor:`.

---

# 2. ViPi TV

## Thiết lập đề xuất hiện tại

- TV: `media_player.beyondtv2`
- Loa thông báo: `media_player.cua_truoc`
- TTS: `tts.edge_tts`
- Trạng thái được tính là đang xem: `playing`
- Khung 1: `10:30-11:30`
- Khung 2: `17:30-18:30`
- Khung 3: `20:30-21:00`
- Tối đa mỗi khung: `30 phút`
- T2-T6: `60 phút/ngày`
- T7-CN: `90 phút/ngày`
- Cấp ngoài giờ: `30 phút`

Mọi giá trị trên đều thay đổi được trong:

```text
Settings → Devices & services → ViPi TV → Configure
```

Không cần sửa code.

## Logic

- Chỉ cộng thời gian khi TV ở đúng state đã cấu hình, mặc định là `playing`.
- Tắt TV rồi bật lại trong cùng khung không reset quota.
- Bắt đầu khung mới mới reset quota khung.
- Tổng ngày không reset khi đổi khung.
- Ngoài giờ mặc định bị chặn.
- Bố mẹ có thể cấp một lượt ngoài giờ.
- Phút ngoài giờ vẫn cộng vào tổng ngày.
- Tổng ngày luôn có ưu tiên cao nhất.
- Dữ liệu thời gian được lưu local để HA restart không mất.
- 00:00 reset tổng ngày.

## Entity chính

Tên entity có thể được HA thêm hậu tố nếu trùng tên. Mặc định:

```text
sensor.vipi_tv_da_xem_hom_nay
sensor.vipi_tv_con_lai_hom_nay
sensor.vipi_tv_da_xem_khung_hien_tai
sensor.vipi_tv_con_lai_khung_hien_tai
sensor.vipi_tv_con_lai_ngoai_gio
sensor.vipi_tv_trang_thai

switch.vipi_tv_quan_ly
switch.vipi_tv_quyen_xem_ngoai_gio

button.vipi_tv_tang_5_phut
button.vipi_tv_giam_5_phut
button.vipi_tv_cho_xem_ngoai_gio
button.vipi_tv_huy_xem_ngoai_gio
button.vipi_tv_reset_hom_nay
```

## Card TV

Copy nguyên file:

```text
dashboard_cards/card_vipi_tv.yaml
```

---

# 3. ViPi Alarm

Mỗi config entry là một báo thức riêng. Có thể tạo nhiều báo thức bằng cách Add Integration `ViPi Alarm` nhiều lần.

Ví dụ báo thức hiện tại:

```text
Tên: Báo thức đi học
Giờ: 06:00
Ngày: mon,tue,wed,thu,fri
Nội dung: Chào buổi sáng, dậy đi học đi các con.
Loa: media_player.cua_truoc
TTS: tts.edge_tts

Đọc thứ/ngày: Có
Đọc lịch âm: Có
Nhắc mùng 1/rằm: Có
Đọc giờ tốt: Có
Đọc giờ xấu: Có
```

Có thể thay đổi tất cả trong `Configure`.

Entity:

```text
switch.vipi_alarm_bao_thuc_di_hoc
button.vipi_alarm_bao_thuc_di_hoc_phat_thu
sensor.vipi_alarm_bao_thuc_di_hoc_lan_tiep_theo
```

Card mẫu:

```text
dashboard_cards/card_vipi_alarm.yaml
```

---

# 4. ViPi Schedule

Mỗi config entry là một lịch nhắc riêng. Có thể thêm bao nhiêu lịch tùy ý.

Ví dụ nên tạo 4 lịch:

```text
1. Minh Châu - Tiếng Anh - mon - 17:30
2. Minh Châu - Tiếng Anh - sun - 16:30
3. Minh Anh  - Tiếng Anh - tue - 19:45
4. Minh Anh  - Tiếng Anh - sun - 15:15
```

Mỗi lịch có các mốc nhắc tùy chọn:

```text
- 21:00 tối hôm trước
- 06:30 sáng ngày học
- trước giờ học N phút, mặc định 15 phút
```

Có thể bật/tắt từng lịch bằng switch và sửa giờ/ngày/nội dung bằng `Configure`.

Entity mỗi lịch:

```text
switch.<ten_lich>
button.<ten_lich>_nhac_thu
sensor.<ten_lich>_lan_tiep_theo
```

Card mẫu:

```text
dashboard_cards/card_vipi_schedule.yaml
```

---

# 5. Lịch âm

Engine `lich_am` dùng thuật toán âm lịch Việt Nam Hồ Ngọc Đức / Jean Meeus, GMT+7.

Bản này sửa lỗi của code cũ ở phần giờ tốt/xấu: giờ Hoàng đạo/Hắc đạo được chọn theo Chi của ngày và trả đủ 6 giờ tốt + 6 giờ xấu.

Entity:

```text
sensor.am_lich_hom_nay
sensor.ngay_am_hom_nay
sensor.can_chi_ngay
sensor.gio_tot_hom_nay
sensor.gio_xau_hom_nay
sensor.am_lich_ngay_mai
```

---

# 6. Khôi phục nhanh sau khi HA lỗi

1. Cài lại Home Assistant.
2. Chép lại 4 thư mục `custom_components`.
3. Thêm sensor `lich_am` vào `configuration.yaml`.
4. Restart.
5. Add Integration `ViPi TV`.
6. Add Integration `ViPi Alarm`.
7. Add Integration `ViPi Schedule` cho từng lịch.
8. Mở README này và nhập lại các preset ở trên.
9. Copy card từ thư mục `dashboard_cards`.

Không phải viết lại automation YAML.

---

# 7. Trước khi bật ViPi TV mới

Hãy tắt các automation TV trẻ em cũ để tránh chạy song song và đếm hai lần.

Đặc biệt các automation cũ có tên gần giống:

```text
TV trẻ em đếm thời gian xem
TV trẻ em đếm thời gian xem 2
TV trẻ em hết 30 phút trong khung
TV trẻ em hết 60 phút trong ngày
TV trẻ em hết thời gian trong ngày
TV trẻ em bảo vệ định kỳ
TV trẻ em bảo vệ ngoài giờ
TV trẻ em chặn ngoài khung giờ
TV trẻ em reset bộ đếm khung
TV trẻ em reset thời gian hàng ngày
```

Chỉ tắt automation TV cũ. Không đụng vào automation khác trong nhà.

---

# 8. Lưu ý trạng thái TV

ViPi TV mặc định tính khi entity TV có state:

```text
playing
```

Nếu video đang phát nhưng số phút không tăng:

```text
Developer Tools → States → media_player.beyondtv2
```

Xem state thực tế là gì. Nếu TV của bạn dùng `on`, hãy vào `ViPi TV → Configure` và đổi `Trạng thái được tính là đang xem` thành `on`.

Nếu entity đúng là `media_player.tv_phong_khach`, chỉ việc chọn lại entity đó trong Configure; không sửa code.



## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Homeassistant
# custom_components lịch âm
Tải thư mục lịch âm và chép vào thư mục custom_components trong hass


Thêm trong configuration:

```sh
sensor:
  - platform: lich_am

```

Thêm trong automation
```sh
automation:
  # Auto Nhắc rằm và mùng 1 qua ViPi vào 6h sáng và 18h tối vào trước 1 ngày và ngày rằm + mùng 1
  - id: '0001'
    alias: Nhắc rằm mùng 1
    trigger:
      - platform: time
        at: '06:00:00'
      - platform: time
        at: '18:00.:00'
    action:
      - service: script.phat_loa_vipi
        data_template:
          message: >           
            {% set ngay_mai = states('sensor.am_lich_ngay_mai') %}
            {% set ngay_mai_int = ngay_mai.split('/')[0] | int %}
            {% set ngay_hom_nay = states('sensor.am_lich_hom_nay') %}
            {% set ngay_hom_nay_int = ngay_hom_nay.split('/')[0] | int %}
            {% if ngay_mai_int == 1 %}
              "Bản tin thông báo: Ngày mai là mùng 1 âm lịch. Nhằm {{ states('sensor.ngay_am_ngay_mai') }}."
              "giờ tốt {{ states('sensor.gio_tot_ngay_mai') }} giờ xấu là giờ: {{ states('sensor.gio_xau_ngay_mai') }}."
            {% elif ngay_mai_int == 15 %}
              "Bản tin thông báo: Ngày mai là rằm. Nhằm {{ states('sensor.ngay_am_ngay_mai') }}."
              " ngày mai {{ states('sensor.gio_tot_ngay_mai') }} giờ xấu là giờ:{{ states('sensor.gio_xau_ngay_mai') }}."
            {% elif ngay_hom_nay_int == 15 %}
              "Bản tin thông báo: Hôm nay là rằm. Nhằm  {{ states('sensor.ngay_am_hom_nay') }}."
              "giờ tốt là giờ: {{ states('sensor.gio_tot_hom_nay') }} giờ xấu là giờ: {{ states('sensor.gio_xau_hom_nay') }}."
            {% elif ngay_hom_nay_int == 1 %}
              "Bản tin thông báo: Hôm nay là mùng 1. Nhằm {{ states('sensor.ngay_am_hom_nay') }}."
              "giờ tốt là giờ: {{ states('sensor.gio_tot_hom_nay') }} giờ xấu là giờ: {{ states('sensor.gio_xau_hom_nay') }}."
            {% endif %}  

   ```
# custom_components edge_tts
Tải thư mục edge_tts và chép vào thư mục custom_components trong hass


Thêm trong configuration:
```sh
tts:
  - platform: edge_tts
    service_name: edge
    language: vi-VN-HoaiMyNeural
    volume: +10%
    rate: -10%

   ```
Ví dụ về scrip phát giọng Nữ edge-tts qua loa google
```sh
  phat_loa_phong_khach:
    alias: "script phat loa phòng khách"
    sequence:
      - service: media_player.volume_set
        target:
          entity_id: media_player.phong_khach_2
        data_template:
          volume_level: "{{ volume | default(0.5) }}"  # Sử dụng giá trị mặc định là 0.5 nếu không có giá trị được cung cấp
      - service: tts.edge
        data_template:
          entity_id: media_player.phong_khach_2
          message: "{{ message }}"

  test_script_media_pk:
    alias: Test script phát media player phòng khách
    sequence:
      - service: script.phat_loa_phong_khach
        data:
          message: 'đây là scrip test loa media player phòng khách'
          volume: 0.5  # Thay 0.5 bằng mức âm lượng mong muốn (giữa 0 và 1)
   ```
