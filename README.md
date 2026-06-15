# Vesper — Drone Mission Control

Sistema de coordenação de frotas de drones para operações de cidade inteligente em Maricá/RJ. Desenvolvido como projeto de arquitetura de software aplicada, cobrindo Clean Architecture, microsserviços, padrões GoF, TDD, BDD e Docker do zero à produção.

---

## O Problema

Maricá opera drones para monitoramento de enchentes, patrulha costeira, entrega de emergência e vigilância de tráfego. O desafio não é apenas voar — é coordenar múltiplos drones com tipos e capacidades diferentes, calcular rotas com trade-offs distintos (velocidade vs segurança vs bateria), registrar eventos em tempo real e garantir que nenhuma missão colida com outra. Um drone marcado como IDLE num registro e ATIVO em outro é um acidente esperando para acontecer.

A solução precisa de um estado global confiável, criação de drones por tipo sem if/else, troca de algoritmo de rota em runtime, notificação desacoplada de eventos e isolamento total da lógica de negócio do framework web.

---

## Arquitetura — Microsserviços

O sistema é dividido em dois serviços independentes com bancos separados, comunicando-se via HTTP, com nginx como API gateway.

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend  :5173                          │
│              React 18 · Vite · TailwindCSS                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP
                       ┌───────▼────────┐
                       │  nginx :8000   │  ← API Gateway
                       │  (port 80)     │
                       └───┬───────┬────┘
                           │       │
            /api/drones/   │       │  /api/missions/
                           │       │  /api/system/
               ┌───────────▼─┐   ┌─▼───────────────┐
               │drone-service│   │ mission-service  │
               │   :8001     │◄──│    :8002         │
               │             │   │ HttpDroneRepo    │
               └──────┬──────┘   └────────┬─────────┘
                      │                   │
               ┌──────▼──────┐   ┌────────▼─────────┐
               │  db-drones  │   │   db-missions    │
               │ PostgreSQL  │   │   PostgreSQL      │
               └─────────────┘   └──────────────────┘
```

**drone-service** gerencia a frota: cadastro, status e bateria dos drones. Expõe `GET /api/drones/`, `GET /api/drones/{id}/` e `PATCH /api/drones/{id}/status/`.

**mission-service** contém toda a lógica de negócio: casos de uso, padrões GoF, estratégias de rota, observers e o ciclo de vida das missões. Quando precisa de dados de um drone, chama o drone-service via HTTP — sem compartilhar banco nem modelo Django.

A comunicação inter-serviço é feita pelo `HttpDroneRepository`, que implementa a mesma interface abstrata `DroneRepository` que o monolito usava com ORM. O `StartMissionUseCase` não sabe — e não precisa saber — se os dados do drone vêm de um banco local ou de uma chamada HTTP.

---

## Arquitetura Limpa

```
mission-service/
├── domain/                 ← Entidades puras e contratos (sem Django, sem requests)
│   ├── entities/
│   │   ├── drone.py        ← DroneEntity (dataclass)
│   │   └── mission.py      ← MissionEntity (dataclass)
│   └── repositories/
│       ├── drone_repository.py    ← ABC: get_by_id, save, list_all
│       └── mission_repository.py  ← ABC: create, log_event, update_status
│
├── application/            ← Casos de uso (depende só de domain/)
│   └── use_cases/
│       └── start_mission_use_case.py
│
├── infrastructure/         ← Implementações concretas (ORM, HTTP)
│   └── repositories/
│       ├── django_mission_repository.py  ← Mission via Django ORM
│       └── http_drone_repository.py      ← Drone via HTTP para drone-service
│
└── adapters/               ← Interface com o mundo externo (views Django)
    ├── views/
    └── urls/
```

A regra de dependência é respeitada: camadas internas não importam camadas externas. `StartMissionUseCase` importa `DroneRepository` (domain). `HttpDroneRepository` importa `DroneRepository` (domain) e faz chamadas HTTP (infrastructure). A inversão de dependência garante que trocar de ORM para HTTP não exigiu mudar uma linha no caso de uso.

---

## SOLID

**Single Responsibility** — cada classe faz uma coisa. `DroneMissionFacade` orquestra; `StartMissionUseCase` valida e persiste; `HttpDroneRepository` faz chamadas HTTP; `LoggerObserver` escreve logs. Nenhuma dessas classes sabe da existência das outras diretamente.

**Open/Closed** — adicionar um novo tipo de drone é criar uma subclasse de `DroneFactory` sem tocar nas existentes. Adicionar uma nova estratégia de rota é implementar `RouteStrategy`. Adicionar um novo observer é implementar `MissionObserverInterface`. Nenhum código existente muda.

**Liskov Substitution** — qualquer `RouteStrategy` pode ser passada para o caso de uso e o resultado é um `RouteResult` válido. Qualquer `DroneRepository` (ORM ou HTTP) pode ser injetado na `DroneMissionFacade` e o comportamento é o esperado — os testes com `FakeDroneRepository` provam isso.

**Interface Segregation** — `DroneRepository` expõe `get_by_id`, `save` e `list_all`. `MissionRepository` expõe `create`, `get_by_id`, `log_event` e `update_status`. As interfaces são pequenas e específicas; nenhuma implementação é forçada a implementar métodos que não usa.

**Dependency Inversion** — `StartMissionUseCase` recebe `DroneRepository` e `MissionRepository` como parâmetros. `DroneMissionFacade` recebe os repositórios no construtor com default para as implementações concretas. Isso permite injetar fakes nos testes sem nenhum mock de framework.

```python
# O caso de uso não importa Django nem requests — só abstrações
class StartMissionUseCase:
    def __init__(self, drone_repo: DroneRepository, mission_repo: MissionRepository):
        self._drone_repo = drone_repo
        self._mission_repo = mission_repo
```

---

## Padrões de Projeto (GoF)

### Singleton — `MissionControlCenter`

Um estado global compartilhado por todos os subsistemas: quais drones estão ativos, quais missões estão em andamento, log de eventos. Dois registros divergentes causariam double-dispatch — um drone IDLE num registro e ATIVO em outro resultaria em missões concorrentes no mesmo hardware.

```python
class MissionControlCenter:
    _instance: Optional[MissionControlCenter] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> MissionControlCenter:
        if cls._instance is None:
            cls()
        return cls._instance
```

---

### Factory Method — `DroneFactory`

Surveillance, Emergency e Delivery têm specs de hardware radicalmente diferentes. Sem factory, cada criação de drone seria um bloco `if/elif` com os defaults hardcoded no meio do código de negócio. Com factory, adicionar um `MedicalDroneFactory` não toca em nenhuma linha existente.

```
DroneFactory (abstract)
  ├── SurveillanceDroneFactory  →  Vesper-S400 Sentinel   95 km/h · 60 km · 0.5 kg payload
  ├── EmergencyDroneFactory     →  Vesper-E200 Raptor    140 km/h · 35 km · 2.0 kg payload
  └── DeliveryDroneFactory      →  Vesper-D800 Carrier    65 km/h · 25 km · 8.0 kg payload
```

Cada factory implementa `create_drone() → DroneConfig`. O `DroneConfig` é um value object imutável — a factory cria, o caller usa.

---

### Strategy — `RouteStrategy`

Velocidade, segurança e economia de bateria são trade-offs que variam por missão, não por tipo de drone. O operador escolhe no momento da criação da missão qual algoritmo usar. Em runtime, o caso de uso recebe a string da estratégia e seleciona a implementação via dicionário:

```
FastestRouteStrategy    — rota direta, ignora risco climático       weather_risk: 0.45
SafeRouteStrategy       — desvio por espaço aéreo limpo             weather_risk: 0.10
BatterySavingStrategy   — rota costeira baixa altitude              weather_risk: 0.25
```

Cada estratégia recebe `(origin, destination, speed_kmh, range_km)` e retorna um `RouteResult` com duração estimada, distância, consumo de bateria, risco climático e waypoints.

---

### Observer — `MissionSubject` + Observers

Quando um evento ocorre numa missão (bateria baixa, missão concluída, obstáculo detectado), três sistemas precisam reagir de forma independente: o logger escreve no terminal, o alert buffer armazena para o operador, e o status observer sincroniza o banco e o Singleton. Acoplamento direto entre esses sistemas seria impossível de manter.

```
MissionSubject.notify(event)
  ├── LoggerObserver         → loguru structured log
  ├── AlertObserver          → buffer de alertas para o frontend
  └── MissionStatusObserver  → atualiza Mission.status no banco + Singleton
```

Adicionar `SlackNotifierObserver` ou `WebhookObserver` é implementar a interface e chamar `subject.attach()`. O subject não muda.

---

### Facade — `DroneMissionFacade`

Sem facade, a view HTTP precisaria conhecer DroneRepository, StartMissionUseCase, threading, MissionSubject e os três observers. A view ficaria com 60+ linhas de orquestração. Com facade, a view faz uma chamada:

```python
facade = DroneMissionFacade()
result = facade.create_and_start_mission(payload)
```

Internamente: valida o drone → calcula rota → persiste missão → atualiza drone → registra no Singleton → dispara eventos → inicia thread de ciclo de vida. Tudo escondido. A view não sabe que existe uma thread em background.

No contexto de microsserviços, a única mudança na Facade foi `HttpDroneRepository()` no lugar de `DjangoDroneRepository()`. O `StartMissionUseCase` não mudou nenhuma linha.

---

## TDD

164 testes cobrindo todas as camadas, escritos antes ou junto com o código.

```
tests/
├── unit/
│   ├── test_strategies.py          # 27 testes — fórmulas de cada estratégia
│   ├── test_factories.py           # 23 testes — specs dos 3 tipos de drone
│   ├── test_observers.py           # 16 testes — lógica de alert buffer e logger
│   ├── test_events.py              # 10 testes — attach/detach/notify do subject
│   ├── test_singleton.py           # 21 testes — instância única, registro, estatísticas
│   └── test_start_mission_use_case.py  # 21 testes — use case com repositórios fake
│
└── integration/
    ├── test_api_drones.py          #  9 testes — endpoints HTTP de drones
    ├── test_api_missions.py        # 15 testes — endpoints HTTP de missões
    └── test_facade.py              #  9 testes — facade end-to-end com banco SQLite
```

Os testes de `StartMissionUseCase` usam `FakeDroneRepository` e `FakeMissionRepository` — implementações em memória das ABCs de domínio. Sem mock de framework, sem patch, sem acesso a banco. Isso é possível exatamente porque a Dependency Inversion foi aplicada corretamente.

```bash
cd backend
.venv/bin/pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## BDD

Cenários de comportamento escritos em Gherkin, executados com pytest-bdd.

```
backend/features/
├── route_strategy.feature      # Dado que um drone tem velocidade X, quando calcula rota SAFE...
├── drone_factory.feature       # Dado que crio um drone SURVEILLANCE, então speed_kmh deve ser 95
├── mission_lifecycle.feature   # Dado um drone IDLE, quando inicio missão, então status vira ACTIVE
└── alert_observer.feature      # Dado evento BAD_WEATHER com severity ALERT, então buffer não vazio
```

Exemplo de cenário:

```gherkin
Feature: Route Strategy Selection

  Scenario: Safe route avoids weather risk
    Given a drone with speed 95 km/h and range 60 km
    When I calculate a SAFE route to "Itaipuaçu"
    Then the weather risk score should be below 0.20
    And the route should include an intermediate waypoint
```

```bash
cd backend
.venv/bin/pytest tests/bdd/ -v
```

---

## Docker

Seis containers orquestrados com dependências e healthchecks encadeados:

```yaml
db-drones      # PostgreSQL para drone-service
db-missions    # PostgreSQL para mission-service
drone-service  # Django :8001 — aguarda db-drones healthy
mission-service# Django :8002 — aguarda db-missions + drone-service healthy
nginx          # API gateway :8000 — aguarda ambos os serviços healthy
frontend       # React/Vite :5173 — aguarda nginx healthy
```

O `depends_on` com `condition: service_healthy` garante que nenhum serviço sobe antes do que ele depende estar respondendo. O drone-service roda `seed_drones` no primeiro boot via Factory Method, criando 6 drones nos 3 tipos.

---

## Como rodar

**Pré-requisito:** Docker e Docker Compose instalados.

```bash
git clone <repo>
cd vesper-drone-mission-control
cp .env.example .env
docker compose up --build
```

A ordem de inicialização é automática. Quando todos os containers estiverem healthy:

| Serviço | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API Gateway | http://localhost:8000/api/ |
| drone-service (direto) | http://localhost:8001/api/drones/ |
| mission-service (direto) | http://localhost:8002/api/missions/ |

Para parar sem perder dados:
```bash
docker compose down
```

Para resetar tudo (apaga bancos):
```bash
docker compose down -v
```

---

## API

| Método | Endpoint | Serviço |
|---|---|---|
| GET | `/api/drones/` | drone-service |
| GET | `/api/drones/{id}/` | drone-service |
| PATCH | `/api/drones/{id}/status/` | drone-service (interno) |
| GET | `/api/missions/` | mission-service |
| POST | `/api/missions/create/` | mission-service |
| GET | `/api/missions/{id}/` | mission-service |
| GET | `/api/missions/logs/` | mission-service |
| GET | `/api/system/status/` | mission-service |
| GET | `/api/system/metadata/` | mission-service |

Payload para criar missão:

```json
{
  "name": "Flood Watch Alpha",
  "mission_type": "FLOOD_MONITORING",
  "region": "Itaipuaçu",
  "priority": "HIGH",
  "drone_id": "<uuid>",
  "route_strategy": "SAFE"
}
```

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, Axios |
| Backend | Python 3.12, Django 5, Django REST Framework |
| Banco | PostgreSQL 16 (dois bancos separados) |
| Gateway | nginx alpine |
| Testes | pytest, pytest-django, pytest-bdd, pytest-cov |
| Logging | loguru, Rich |
| Container | Docker, Docker Compose |
| Deploy | — |

---

## Decisões de arquitetura

**Por que dois bancos separados?** Microsserviços que compartilham banco não são microsserviços — são um monolito com processo separado. Bancos separados garantem que uma migração no `missions` nunca afeta o schema de `drones`, e cada serviço pode escalar o banco de forma independente.

**Por que nginx como gateway e não chamar os serviços diretamente?** O frontend faz requisições para uma URL só. O gateway decide o roteamento. Se amanhã `drone-service` mudar de porta ou hostname, o frontend não muda nada — só o nginx.conf muda.

**Por que o monolito `backend/` foi mantido?** Ele contém os 164 testes (TDD/BDD) e toda a evidência de Clean Architecture que seria trabalhosa de replicar nos dois serviços separados. Os serviços em `services/` demonstram a separação em produção; o `backend/` demonstra a qualidade do código.

**Por que `HttpDroneRepository` em vez de event sourcing ou message broker?** Para o escopo do projeto, HTTP síncrono é suficiente e torna o código legível por qualquer avaliador sem conhecimento de RabbitMQ ou Kafka. A interface abstrata `DroneRepository` permite trocar para mensageria futuramente sem tocar no caso de uso.

---

*Vesper Drone Mission Control · Maricá/RJ*
