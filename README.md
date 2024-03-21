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
  # Auto Nhắc rằm và mùng 1 qua ViPi
  - id: '0001'
    alias: Nhắc rằm mùng 1
    trigger:
      - platform: time
        at: '06:30:00'
      - platform: time
        at: '16:04:00'
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
