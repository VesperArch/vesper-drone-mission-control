from django.core.management.base import BaseCommand
from rich.console import Console
from rich.table import Table

from drones.factories import (
    SurveillanceDroneFactory,
    EmergencyDroneFactory,
    DeliveryDroneFactory,
)
from drones.models import Drone

console = Console()

_DRONE_SEEDS = [
    ("Sentinel Alpha",  SurveillanceDroneFactory()),
    ("Sentinel Beta",   SurveillanceDroneFactory()),
    ("Raptor-1",        EmergencyDroneFactory()),
    ("Raptor-2",        EmergencyDroneFactory()),
    ("Carrier Prime",   DeliveryDroneFactory()),
    ("Carrier Backup",  DeliveryDroneFactory()),
]


class Command(BaseCommand):
    help = "Seed drone-service database with demo drones."

    def handle(self, *args, **kwargs) -> None:
        if Drone.objects.count() >= len(_DRONE_SEEDS):
            console.print("[yellow]Drones already seeded — skipping.[/yellow]")
            return

        created = []
        for name, factory in _DRONE_SEEDS:
            config = factory.build()
            drone = Drone.objects.create(
                name=name,
                model=config.model,
                drone_type=config.drone_type,
                speed_kmh=config.speed_kmh,
                altitude_limit_m=config.altitude_limit_m,
                payload_kg=config.payload_kg,
                range_km=config.range_km,
                description=config.description,
                battery_level=100.0,
            )
            created.append(drone)

        table = Table(title="Drone Fleet — drone-service", border_style="cyan")
        table.add_column("Name", style="bold white")
        table.add_column("Type", style="cyan")
        table.add_column("Speed km/h", justify="right")
        table.add_column("Range km", justify="right")
        for d in created:
            table.add_row(d.name, d.drone_type, str(d.speed_kmh), str(d.range_km))

        console.print(table)
        console.print(f"[green]✓[/green] Seeded {len(created)} drones into drone-service.")
