"""
Demo seed command — populates the DB with drones using the Factory Method
pattern, then runs two sample missions through the Facade.

Run:  python manage.py seed_demo
"""

from django.core.management.base import BaseCommand
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from drones.factories import (
    SurveillanceDroneFactory,
    EmergencyDroneFactory,
    DeliveryDroneFactory,
)
from drones.models import Drone
from core.singleton import MissionControlCenter
from core.singleton.mission_control_center import DroneRecord
from core.facade import DroneMissionFacade

console = Console()


_DRONE_SEEDS = [
    ("Sentinel Alpha",   SurveillanceDroneFactory()),
    ("Sentinel Beta",    SurveillanceDroneFactory()),
    ("Raptor-1",         EmergencyDroneFactory()),
    ("Raptor-2",         EmergencyDroneFactory()),
    ("Carrier Prime",    DeliveryDroneFactory()),
    ("Carrier Backup",   DeliveryDroneFactory()),
]


class Command(BaseCommand):
    help = "Seed the database with demo drones and run sample missions."

    def handle(self, *args, **kwargs) -> None:
        console.print(Panel.fit(
            "[bold cyan]Vesper Drone Mission Control[/bold cyan]\n"
            "[dim]Demo seed — populating operational data[/dim]",
            border_style="cyan",
        ))

        # ── Singleton: fetch or create control centre ─────────────────────
        control = MissionControlCenter.get_instance()
        console.print(f"\n[green]✓[/green] MissionControlCenter online: {control}")

        # ── Factory Method: create drones ─────────────────────────────────
        console.print("\n[bold]Creating drone fleet via Factory Method...[/bold]")
        created_drones: list[Drone] = []

        if Drone.objects.count() >= len(_DRONE_SEEDS):
            console.print("[yellow]Drones already seeded — skipping creation.[/yellow]")
            created_drones = list(Drone.objects.all())
        else:
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
                created_drones.append(drone)
                control.register_drone(DroneRecord(
                    drone_id=str(drone.id),
                    drone_name=drone.name,
                    drone_type=drone.drone_type,
                    status=drone.status,
                    battery_level=drone.battery_level,
                ))

        table = Table(title="Registered Fleet", border_style="cyan")
        table.add_column("Name", style="bold white")
        table.add_column("Model", style="dim")
        table.add_column("Type", style="cyan")
        table.add_column("Speed (km/h)", justify="right")
        table.add_column("Range (km)", justify="right")

        for d in created_drones:
            table.add_row(d.name, d.model, d.drone_type, str(d.speed_kmh), str(d.range_km))

        console.print(table)

        # ── Facade: run sample missions ───────────────────────────────────
        console.print("\n[bold]Running sample missions via DroneMissionFacade...[/bold]")
        facade = DroneMissionFacade()

        sample_missions = [
            {
                "name": "Flood Watch Alpha",
                "mission_type": "FLOOD_MONITORING",
                "region": "Itaipuaçu",
                "priority": "HIGH",
                "drone_id": str(created_drones[0].id),
                "route_strategy": "SAFE",
            },
            {
                "name": "Emergency Drop Beta",
                "mission_type": "EMERGENCY_DELIVERY",
                "region": "Ponta Negra",
                "priority": "CRITICAL",
                "drone_id": str(created_drones[4].id),
                "route_strategy": "FASTEST",
            },
        ]

        for payload in sample_missions:
            result = facade.create_and_start_mission(payload)
            if "error" not in result:
                console.print(f"  [green]✔[/green] Mission '{payload['name']}' → {result.get('status')}")
            else:
                console.print(f"  [red]✗[/red] {result['error']}")

        # ── Final stats ───────────────────────────────────────────────────
        stats = control.get_statistics()
        console.print(Panel(
            f"[bold]System Statistics[/bold]\n"
            f"Total missions : {stats['total_missions']}\n"
            f"Active         : {stats['active_missions']}\n"
            f"Completed      : {stats['completed_missions']}\n"
            f"Events fired   : {stats['total_events_fired']}",
            title="MissionControlCenter",
            border_style="green",
        ))
