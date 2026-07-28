#!/usr/bin/env python3

import argparse
import logging
from signal import pause
from threading import Lock


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("no-touch-sensor")

# Menyimpan status agar "SELAMAT JALAN" hanya muncul
# setelah sebelumnya ada deteksi "SELAMAT DATANG".
sensor_active = False
state_lock = Lock()


def sensor_on() -> None:
    """Tampilkan sambutan ketika tangan/objek mulai terdeteksi."""
    global sensor_active

    with state_lock:
        if sensor_active:
            return

        sensor_active = True
        logger.info(
            "SELAMAT DATANG | SENSOR=ON | INDICATOR=GREEN | HAND=DETECTED"
        )


def sensor_off() -> None:
    """Tampilkan salam perpisahan ketika tangan/objek tidak terdeteksi lagi."""
    global sensor_active

    with state_lock:
        if not sensor_active:
            return

        sensor_active = False
        logger.info(
            "SELAMAT JALAN | SENSOR=OFF | INDICATOR=NORMAL | HAND=NOT_DETECTED"
        )


def run_mock_mode() -> None:
    """
    Mode simulasi untuk pengujian di laptop/komputer
    tanpa Raspberry Pi dan tanpa sensor.
    """
    logger.info("NO-TOUCH SENSOR MOCK MODE STARTED")
    logger.info("Ketik 'on' untuk SELAMAT DATANG, 'off' untuk SELAMAT JALAN.")

    while True:
        command = input("sensor> ").strip().lower()

        if command == "on":
            sensor_on()

        elif command == "off":
            sensor_off()

        elif command in {"exit", "quit", "q"}:
            logger.info("Application stopped.")
            break

        else:
            logger.warning(
                "Perintah tidak dikenal. Gunakan: on, off, atau exit."
            )


def run_gpio_mode(gpio_pin: int) -> None:
    """
    Mode GPIO untuk dijalankan pada Raspberry Pi.
    Relay sensor dihubungkan ke GPIO dan GND.
    """
    try:
        from gpiozero import Button
    except ImportError:
        logger.error("Library gpiozero belum terpasang.")
        logger.error(
            "Jalankan: sudo apt install python3-gpiozero python3-lgpio"
        )
        return

    sensor = Button(
        gpio_pin,
        pull_up=True,
        bounce_time=0.2,
    )

    sensor.when_pressed = sensor_on
    sensor.when_released = sensor_off

    logger.info("NO-TOUCH SENSOR GPIO MODE STARTED")
    logger.info("GPIO=%s | STATUS=READY", gpio_pin)
    logger.info("Waiting for hand detection...")

    if sensor.is_pressed:
        sensor_on()

    try:
        pause()
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    finally:
        sensor.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="No-Touch Sensor Button Logger"
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Menjalankan simulasi tanpa sensor",
    )

    parser.add_argument(
        "--pin",
        type=int,
        default=17,
        help="Nomor GPIO BCM. Default: GPIO17",
    )

    args = parser.parse_args()

    if args.mock:
        run_mock_mode()
    else:
        run_gpio_mode(args.pin)


if __name__ == "__main__":
    main()