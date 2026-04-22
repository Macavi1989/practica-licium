# **Practica Licium**

## **Nivel 1 - practice_checklist**

Un módulo en Licium se divide en 4 capas: los modelos que definen las tablas de la base de datos y generan la API automáticamente, los servicios que contienen la lógica de negocio más allá del CRUD básico (como cerrar una checklist o marcar un ítem como hecho), las vistas y menú en YAML que definen cómo se ve todo en el panel de administración, y la seguridad con grupos y ACL que controla quién puede hacer qué. En este nivel construimos el módulo practice_checklist desde cero, lo instalamos con Docker y lo subimos a GitHub, aprendiendo así el flujo completo de desarrollo de un módulo real en Licium.

## **Nivel 2 - asset_lending**

En este nivel implementamos un módulo de gestión de préstamos de equipamiento interno con tres modelos relacionados: Location (ubicaciones), Asset (recursos como portátiles o cámaras) y Loan (préstamos). Se desarrollaron acciones de servicio para controlar el ciclo de vida de cada recurso: sacarlo en préstamo, devolverlo y enviarlo a mantenimiento, validando en cada paso que el estado del recurso sea el correcto. También se configuró una ACL avanzada con dominio para que un grupo técnico solo pueda modificar recursos de su propia ubicación.

## **Nivel 3 - feedback_moderation**

Este módulo implementa un sistema de sugerencias con moderación, donde los usuarios públicos pueden enviar sugerencias y los moderadores las publican, rechazan o fusionan. Se trabajó con tres modelos (Suggestion, Comment y Tag), incluyendo una relación muchos a muchos entre sugerencias y etiquetas mediante una tabla intermedia. Las ACL públicas con dominio garantizan que solo el contenido publicado y marcado como público sea visible desde el exterior, separando así la lógica de moderación interna de la exposición pública.

## **Nivel 4 - community_events**

El módulo más complejo, orientado a la gestión de eventos comunitarios con sesiones, inscripciones y control de asistencia. Se implementaron cuatro modelos (Event, Session, Registration y Checkin) con sus relaciones, y dos servicios principales: EventService para gestionar el ciclo de vida del evento y RegistrationService para las inscripciones, incluyendo una acción masiva de check-in (bulk_checkin). Se añadieron además settings configurables desde el admin para controlar el comportamiento del módulo sin tocar el código.
