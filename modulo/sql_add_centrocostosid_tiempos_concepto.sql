-- Añadir centro de costos a Tiempos_Concepto (sin usar migraciones Django)
-- Ejecutar en MySQL sobre la base de datos del proyecto.

ALTER TABLE `Tiempos_Concepto`
  ADD COLUMN `centrocostosId` int(11) NULL DEFAULT NULL AFTER `LineaId`,
  ADD KEY `Tiempos_Concepto_centrocostosId_fk` (`centrocostosId`),
  ADD CONSTRAINT `Tiempos_Concepto_centrocostosId_fk` 
    FOREIGN KEY (`centrocostosId`) REFERENCES `Centros_Costos` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;
