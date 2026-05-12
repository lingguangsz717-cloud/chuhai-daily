# Libraries

- `generate_daily.py`
  - function generate_date: (date_str)
  - function update_index: (date_str)
  - function main: ()
- `generate_daily_report.py`
  - function load_font: (size)
  - function draw_rounded_rect: (draw, xy, radius, fill)
  - function draw_card: (draw, im, y_start, acc_color, item, index)
  - function wrap_text: (text, font, max_width)
  - function generate_region_image: (region, data)
  - function main: ()
- `send_email.py`
  - function get_subscribers: ()
  - function add_subscriber: (email)
  - function send_daily_report: ()
  - function build_email_html: (data)
