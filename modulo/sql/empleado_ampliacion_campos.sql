-- Script MariaDB: ampliación de campos en tabla Empleado
-- Ejecutar manualmente si no usas migrate.

-- Permitir Perfil N/A (administrativos sin categoría Junior/Semi etc.)
ALTER TABLE `Empleado`
  MODIFY COLUMN `PerfilId` int(11) DEFAULT NULL;

-- Nuevos campos
ALTER TABLE `Empleado`
  ADD COLUMN `Genero` varchar(20) DEFAULT NULL COMMENT 'Masculino / Femenino',
  ADD COLUMN `EstadoCivil` varchar(50) DEFAULT NULL,
  ADD COLUMN `NumeroHijos` int(11) DEFAULT NULL,
  ADD COLUMN `TarjetaProfesional` tinyint(1) DEFAULT NULL COMMENT '0=No, 1=Si',
  ADD COLUMN `RH` varchar(10) DEFAULT NULL COMMENT 'Grupo sanguíneo',
  ADD COLUMN `TipoContrato` varchar(20) DEFAULT NULL COMMENT 'Indefinido / Fijo',
  ADD COLUMN `FondoPension` varchar(100) DEFAULT NULL,
  ADD COLUMN `EPS` varchar(100) DEFAULT NULL,
  ADD COLUMN `FondoCesantias` varchar(100) DEFAULT NULL,
  ADD COLUMN `CajaCompensacion` varchar(100) DEFAULT NULL;

-- Nota: Edad y Años en la empresa se calculan en el informe (no se guardan en BD).
