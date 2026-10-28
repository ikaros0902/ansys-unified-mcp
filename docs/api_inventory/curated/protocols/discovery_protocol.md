# discovery_protocol protocol dictionary

- APIKB source key: `discovery_protocol`
- Package: `ansys-api-discovery 1.2.12`
- Interface: discovery gRPC protocol schema
- Snapshot: [`discovery_protocol_api.json`](../../discovery_protocol_api.json)
- Snapshot SHA-256: `356a05dd6bab65e3ceda08d232c839248d091caed2fcb2b09e4d0e4a174a2c44`

> This page describes the captured protobuf schema. It does not confirm product support, host compatibility, or runtime behavior.
> This snapshot records enum type names on fields. It does not list enum members.

## Services and RPC methods

### `ansys.api.discovery.v0.assignments.boltassignment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BoltAssignment` | `CreateBoltAssignment` | `(ansys.api.discovery.v0.assignments.boltassignment.BoltAssignmentCreationRequest) -> ansys.api.discovery.v0.assignments.boltassignment.BoltAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.assignments.fan_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Fan` | `CreateInternalFanAssignment` | `(ansys.api.discovery.v0.assignments.fanassignment.InternalFanAssignmentCreationRequest) -> ansys.api.discovery.v0.assignments.fanassignment.InternalFanAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `CreateExternalFanAssignment` | `(ansys.api.discovery.v0.assignments.fanassignment.ExternalFanAssignmentCreationRequest) -> ansys.api.discovery.v0.assignments.fanassignment.ExternalFanAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeFanAssignment` | `(ansys.api.discovery.v0.ChangeAssignmentRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeExternalFanSpecification` | `(ansys.api.discovery.v0.assignments.fanassignment.ChangeExternalFanSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeFanLocation` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeExternalFanGaugePressure` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeInternalFanInletFace` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeInternalFanIsShrouded` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeInternalFanHubRadius` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeInternalFanTipRadius` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeInternalFanTotalHeat` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Fan` | `ChangeInternalFanSpecifyTotalHeat` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.acceleration_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Acceleration` | `CreateAcceleration` | `(ansys.api.discovery.v0.conditions.acceleration.AccelerationCreationRequest) -> ansys.api.discovery.v0.conditions.acceleration.AccelerationCreationResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationOrientation` | `(ansys.api.discovery.v0.ChangeDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationDX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationDY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationDZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationTranslationalMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationIsFixedDX` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationIsFixedDY` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `ChangeAccelerationIsFixedDZ` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.bearing_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Bearing` | `CreateBearing` | `(ansys.api.discovery.v0.conditions.bearing.BearingCreationRequest) -> ansys.api.discovery.v0.conditions.bearing.BearingCreationResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `ChangeBearingLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `ChangeBearingRadialForce` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `ChangeBearingThrustForce` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `ChangeBearingAngle` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.boltpreload_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BoltPreload` | `CreateBoltPreloadClampForce` | `(ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadClampForceCreationRequest) -> ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `CreateBoltPreloadGripLength` | `(ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadGripLengthCreationRequest) -> ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `CreateBoltPreloadTorque` | `(ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadTorqueCreationRequest) -> ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadSide1Location` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadSide2Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadSpecification` | `(ansys.api.discovery.v0.conditions.boltpreload.ChangeBoltPreloadSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadClampForce` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadGripLength` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadTorque` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadTorqueCoefficient` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadSpecifyBoltDiameter` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `ChangeBoltPreloadShankDiameter` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.condition_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Condition` | `DeleteCondition` | `(ansys.api.discovery.v0.conditions.DeleteConditionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Condition` | `ChangeConditionSuppressionState` | `(ansys.api.discovery.v0.conditions.ChangeConditionSuppressionStateRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Condition` | `ChangeConditionName` | `(ansys.api.discovery.v0.conditions.ChangeConditionNameRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.convection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Convection` | `CreateConvection` | `(ansys.api.discovery.v0.conditions.convection.ConvectionCreationRequest) -> ansys.api.discovery.v0.conditions.convection.ConvectionCreationResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `ChangeConvectionLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `ChangeConvectionCoefficientMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `ChangeConvectionTemperatureMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.current_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Current` | `CreateCurrent` | `(ansys.api.discovery.v0.conditions.current.CurrentCreationRequest) -> ansys.api.discovery.v0.conditions.current.CurrentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `ChangeCurrentLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `ChangeCurrentMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.displacement_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Displacement` | `CreateDisplacementTranslation` | `(ansys.api.discovery.v0.conditions.displacement.DisplacementTranslationCreationRequest) -> ansys.api.discovery.v0.conditions.displacement.DisplacementCreationResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `CreateDisplacementRotation` | `(ansys.api.discovery.v0.conditions.displacement.DisplacementRotationCreationRequest) -> ansys.api.discovery.v0.conditions.displacement.DisplacementCreationResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `CreateDisplacementCombined` | `(ansys.api.discovery.v0.conditions.displacement.DisplacementCombinedCreationRequest) -> ansys.api.discovery.v0.conditions.displacement.DisplacementCreationResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementSpecification` | `(ansys.api.discovery.v0.conditions.displacement.ChangeDisplacementSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementOrientation` | `(ansys.api.discovery.v0.ChangeDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementDX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementDY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementDZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementTranslationalMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementRX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementRY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementRZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementRotationalMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementIsFixedDX` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementIsFixedDY` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementIsFixedDZ` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementIsFixedRX` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementIsFixedRY` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementIsFixedRZ` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementUseRemotePointEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementDistributedRemotePositionX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementDistributedRemotePositionY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `ChangeDisplacementDistributedRemotePositionZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.flow_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Flow` | `CreateFlowVelocityInlet` | `(ansys.api.discovery.v0.conditions.flow.FlowVelocityInletCreationRequest) -> ansys.api.discovery.v0.conditions.flow.FlowVelocityInletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateFlowVelocityOutlet` | `(ansys.api.discovery.v0.conditions.flow.FlowVelocityOutletCreationRequest) -> ansys.api.discovery.v0.conditions.flow.FlowVelocityOutletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateFlowPressureInlet` | `(ansys.api.discovery.v0.conditions.flow.FlowPressureInletCreationRequest) -> ansys.api.discovery.v0.conditions.flow.FlowPressureInletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateFlowPressureOutlet` | `(ansys.api.discovery.v0.conditions.flow.FlowPressureOutletCreationRequest) -> ansys.api.discovery.v0.conditions.flow.FlowPressureOutletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateFlowMassFlowInlet` | `(ansys.api.discovery.v0.conditions.flow.FlowMassFlowInletCreationRequest) -> ansys.api.discovery.v0.conditions.flow.FlowMassFlowInletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateFlowMassFlowOutlet` | `(ansys.api.discovery.v0.conditions.flow.FlowMassFlowOutletCreationRequest) -> ansys.api.discovery.v0.conditions.flow.FlowMassFlowOutletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowVelocityInletMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowVelocityOutletMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowPressureInletMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowPressureOutletMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowMassFlowInletMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowMassFlowOutletMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowTemperatureInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowTemperatureMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowSwirlingInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowSwirlingMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowSpecification` | `(ansys.api.discovery.v0.conditions.flow.ChangeFlowSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `ChangeFlowDirection` | `(ansys.api.discovery.v0.conditions.flow.ChangeFlowDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.fluidinitialtemperature_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FluidInitialTemperature` | `ChangeTemperatureMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.force_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Force` | `CreateForceDistributedTotal` | `(ansys.api.discovery.v0.conditions.force.ForceDistributedTotalCreationRequest) -> ansys.api.discovery.v0.conditions.force.ForceDistributedTotalCreationResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `CreateForceDistributedArea` | `(ansys.api.discovery.v0.conditions.force.ForceDistributedAreaCreationRequest) -> ansys.api.discovery.v0.conditions.force.ForceDistributedAreaCreationResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `CreateForceTorque` | `(ansys.api.discovery.v0.conditions.force.ForceTorqueCreationRequest) -> ansys.api.discovery.v0.conditions.force.ForceTorqueCreationResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceSpecification` | `(ansys.api.discovery.v0.conditions.force.ChangeForceSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceMagnitudeDefinition` | `(ansys.api.discovery.v0.conditions.force.ChangeForceMagnitudeDefinitionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceByReversingDirection` | `(ansys.api.discovery.v0.ChangeCommandRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDefinedByComponentEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedTotalMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedTotalX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedTotalY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedTotalZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedAreaMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedAreaX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedAreaY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedAreaZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceUseRemoteForceEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedRemotePositionX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedRemotePositionY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceDistributedRemotePositionZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceTorqueMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceTorqueX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceTorqueY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ChangeForceTorqueZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `GetForceDistributedByLabel` | `(ansys.api.discovery.v0.conditions.GetByLabelRequest) -> ansys.api.discovery.v0.conditions.force.ForceDistributedDefinition [client_streaming=False, server_streaming=False]` |
| `Force` | `GetForceTorqueByLabel` | `(ansys.api.discovery.v0.conditions.GetByLabelRequest) -> ansys.api.discovery.v0.conditions.force.ForceTorqueDefinition [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.gravity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Gravity` | `ChangeGravityOrientation` | `(ansys.api.discovery.v0.ChangeDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `ChangeGravityDX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `ChangeGravityDY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `ChangeGravityDZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `ChangeGravityTranslationalMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `ChangeGravityUseBuoyancyEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `ChangeGravityIncludeSelfWeightEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `GetByLabel` | `(ansys.api.discovery.v0.conditions.GetByLabelRequest) -> ansys.api.discovery.v0.conditions.gravity.GravityDefinition [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.heat_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Heat` | `CreateHeatVolumetricTotal` | `(ansys.api.discovery.v0.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v0.conditions.heat.HeatTotalCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `CreateHeatVolumetricDistributed` | `(ansys.api.discovery.v0.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v0.conditions.heat.HeatVolumetricDistributedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `CreateHeatSurfaceTotal` | `(ansys.api.discovery.v0.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v0.conditions.heat.HeatTotalCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `CreateHeatSurfaceDistributed` | `(ansys.api.discovery.v0.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v0.conditions.heat.HeatSurfaceDistributedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `ChangeHeatLocation` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `ChangeTotalHeat` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `ChangeHeatPerUnitVolume` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `ChangeHeatPerUnitArea` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `ChangeHeatSpecification` | `(ansys.api.discovery.v0.conditions.heat.ChangeHeatSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.insulated_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Insulated` | `CreateInsulated` | `(ansys.api.discovery.v0.conditions.insulated.InsulatedCreationRequest) -> ansys.api.discovery.v0.conditions.insulated.InsulatedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Insulated` | `ChangeInsulatedLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.localfidelity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `LocalFidelity` | `CreateLocalFidelity` | `(ansys.api.discovery.v0.conditions.localfidelity.LocalFidelityCreationRequest) -> ansys.api.discovery.v0.conditions.localfidelity.LocalFidelityCreationResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `ChangeLocalFidelityLocation` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `ChangeLocalFidelityMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.mass_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Mass` | `CreateMass` | `(ansys.api.discovery.v0.conditions.mass.MassCreationRequest) -> ansys.api.discovery.v0.conditions.mass.MassCreationResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `ChangeMassLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `ChangeMassMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `ChangeMassUseRemotePointEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `ChangeMassRemotePositionX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `ChangeMassRemotePositionY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `ChangeMassRemotePositionZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.moment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Moment` | `CreateMomentLocal` | `(ansys.api.discovery.v0.conditions.moment.MomentCreationRequest) -> ansys.api.discovery.v0.conditions.moment.MomentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `CreateMomentGlobal` | `(ansys.api.discovery.v0.conditions.moment.MomentCreationRequest) -> ansys.api.discovery.v0.conditions.moment.MomentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentSpecification` | `(ansys.api.discovery.v0.conditions.moment.ChangeMomentSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentOrientation` | `(ansys.api.discovery.v0.ChangeDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentLocalX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentLocalY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentLocalZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentGlobalX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentGlobalY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `ChangeMomentGlobalZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.operatingpressure_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `OperatingPressure` | `ChangePressureMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.porous_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Porous` | `CreatePorousIsotropic` | `(ansys.api.discovery.v0.conditions.porous.PorousCreationRequest) -> ansys.api.discovery.v0.conditions.porous.PorousCreationResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `CreatePorousBidirectional` | `(ansys.api.discovery.v0.conditions.porous.PorousCreationRequest) -> ansys.api.discovery.v0.conditions.porous.PorousCreationResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `CreatePorousOrthotropic` | `(ansys.api.discovery.v0.conditions.porous.PorousCreationRequest) -> ansys.api.discovery.v0.conditions.porous.PorousCreationResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousSpecification` | `(ansys.api.discovery.v0.conditions.porous.ChangePorousSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousStreamwiseFlowDirectionReference` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousViscousStreamwiseMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousInertialStreamwiseMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousViscousCrossflowPrimaryMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousInertialCrossflowPrimaryMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousViscousCrossflowSecondaryMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousInertialCrossflowSecondaryMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousThermalInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousSolidPorosity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousSolidDensity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousSolidIsotropicThermalConductivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `ChangePorousSolidSpecificHeat` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.pressure_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Pressure` | `CreatePressure` | `(ansys.api.discovery.v0.conditions.pressure.PressureCreationRequest) -> ansys.api.discovery.v0.conditions.pressure.PressureCreationResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `ChangePressureLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `ChangePressureMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.rotatingfluidzone_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `RotatingFluidZone` | `CreateRotatingFluidZone` | `(ansys.api.discovery.v0.conditions.rotatingfluidzone.RotatingFluidZoneCreationRequest) -> ansys.api.discovery.v0.conditions.rotatingfluidzone.RotatingFluidZoneCreationResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `ChangeRotatingFluidZoneLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `ChangeWallRotationalVelocityMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.solidtemperature_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SolidTemperature` | `CreateTemperatureVolumetric` | `(ansys.api.discovery.v0.conditions.solidtemperature.TemperatureCreationRequest) -> ansys.api.discovery.v0.conditions.solidtemperature.TemperatureCreationResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `CreateTemperatureSurface` | `(ansys.api.discovery.v0.conditions.solidtemperature.TemperatureCreationRequest) -> ansys.api.discovery.v0.conditions.solidtemperature.TemperatureCreationResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `ChangeTemperatureLocation` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `ChangeTemperatureMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.springpreload_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SpringPreload` | `CreateSpringPreloadLongitudinal` | `(ansys.api.discovery.v0.conditions.springpreload.SpringPreloadLongitudinalCreationRequest) -> ansys.api.discovery.v0.conditions.springpreload.SpringPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `CreateSpringPreloadTorsional` | `(ansys.api.discovery.v0.conditions.springpreload.SpringPreloadTorsionalCreationRequest) -> ansys.api.discovery.v0.conditions.springpreload.SpringPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadSide1Location` | `(ansys.api.discovery.v0.ChangeLocationExtendedRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadSide2Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadSpecification` | `(ansys.api.discovery.v0.conditions.springpreload.ChangeSpringPreloadSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadLongitudinalStiffness` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadTorsionalStiffness` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadtype` | `(ansys.api.discovery.v0.conditions.springpreload.ChangeSpringPreloadTypeRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadForce` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadTorque` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadLength` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `ChangeSpringPreloadRotation` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.support_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Support` | `CreateSupportFixed` | `(ansys.api.discovery.v0.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v0.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateSupportHinged` | `(ansys.api.discovery.v0.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v0.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateSupportSliding` | `(ansys.api.discovery.v0.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v0.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateSupportBall` | `(ansys.api.discovery.v0.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v0.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateSupportDisplaced` | `(ansys.api.discovery.v0.conditions.support.SupportDisplacedCreationRequest) -> ansys.api.discovery.v0.conditions.support.SupportDisplacedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportSpecification` | `(ansys.api.discovery.v0.conditions.support.ChangeSupportSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedOrientation` | `(ansys.api.discovery.v0.ChangeDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedDX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedDY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedDZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedRX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedRY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedRZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedIsFixedDX` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedIsFixedDY` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedIsFixedDZ` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedIsFixedRX` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedIsFixedRY` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `ChangeSupportDisplacedIsFixedRZ` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `GetAll` | `(ansys.api.discovery.v0.conditions.support.GetAllRequest) -> ansys.api.discovery.v0.conditions.support.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.symmetry_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Symmetry` | `CreateSymmetry` | `(ansys.api.discovery.v0.conditions.symmetry.SymmetryCreationRequest) -> ansys.api.discovery.v0.conditions.symmetry.SymmetryCreationResponse [client_streaming=False, server_streaming=False]` |
| `Symmetry` | `ChangeSymmetryLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.velocity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Velocity` | `CreateVelocity` | `(ansys.api.discovery.v0.conditions.velocity.VelocityCreationRequest) -> ansys.api.discovery.v0.conditions.velocity.VelocityCreationResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityOrientation` | `(ansys.api.discovery.v0.ChangeDirectionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRotationalMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityIsFixedRX` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityIsFixedRY` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityIsFixedRZ` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityUseRemotePointEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRemotePositionX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRemotePositionY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `ChangeVelocityRemotePositionZ` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.voltage_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Voltage` | `CreateVoltage` | `(ansys.api.discovery.v0.conditions.voltage.VoltageCreationRequest) -> ansys.api.discovery.v0.conditions.voltage.VoltageCreationResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `ChangeVoltageLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `ChangeVoltageMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.conditions.wall_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Wall` | `CreateWallFreeSlip` | `(ansys.api.discovery.v0.conditions.wall.WallFreeSlipCreationRequest) -> ansys.api.discovery.v0.conditions.wall.WallFreeSlipCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `CreateWallStationary` | `(ansys.api.discovery.v0.conditions.wall.WallStationaryCreationRequest) -> ansys.api.discovery.v0.conditions.wall.WallStationaryCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `CreateWallTranslating` | `(ansys.api.discovery.v0.conditions.wall.WallTranslationCreationRequest) -> ansys.api.discovery.v0.conditions.wall.WallTranslationCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `CreateWallRotating` | `(ansys.api.discovery.v0.conditions.wall.WallRotationCreationRequest) -> ansys.api.discovery.v0.conditions.wall.WallRotationCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallSpecification` | `(ansys.api.discovery.v0.conditions.wall.ChangeWallSpecificationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallLocation` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallRotationalVelocityMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallTranslationalVelocityMagnitude` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallTranslationalVelocityX` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallTranslationalVelocityY` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallThermalInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallThermalOption` | `(ansys.api.discovery.v0.conditions.wall.ChangeWallThermalOptionRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallInternalRadiationInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallExternalRadiationInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallInternalEmissivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallExternalTemperature` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallConvectionCoefficient` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallHeatFlux` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallHeatFlow` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallTemperature` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `ChangeWallExternalEmissivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.connections.contact_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Contact` | `CreateContact` | `(ansys.api.discovery.v0.connections.contact.ContactCreationRequest) -> ansys.api.discovery.v0.connections.contact.ContactCreationResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactSide1Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactSide2Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactType` | `(ansys.api.discovery.v0.connections.contact.ChangeContactTypeRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactPairs` | `(ansys.api.discovery.v0.connections.contact.ChangeContactPairRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SplitContact` | `(ansys.api.discovery.v0.ChangeEmptyRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactFrictionCoefficient` | `(ansys.api.discovery.v0.ChangeDoubleRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactStiffnessFactor` | `(ansys.api.discovery.v0.ChangeDoubleRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactDetectionRadiusFactor` | `(ansys.api.discovery.v0.ChangeDoubleRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactOffset` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactShearStrength` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactTensileStrength` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactAreStrengthLimitsSet` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactAdjustGapOrOverlap` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactMakeJustTouching` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactIdealize` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactSpecifyThermalConductance` | `(ansys.api.discovery.v0.ChangeSpecifyConductanceRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactSpecifyElectricConductance` | `(ansys.api.discovery.v0.ChangeSpecifyConductanceRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactConductanceThickness` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactConductanceMaterial` | `(ansys.api.discovery.v0.ChangeAssignmentRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactThermalContactConductivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactElectricContactConductivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactThermalContactConductance` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `ChangeContactElectricContactConductance` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.connections.contactgroup_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `ContactGroup` | `ChangeContactGroupSide1Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupSide2Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupContactType` | `(ansys.api.discovery.v0.connections.contact.ChangeContactTypeRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SplitContactGroup` | `(ansys.api.discovery.v0.ChangeEmptyRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ConvertContactGroup` | `(ansys.api.discovery.v0.connections.contactgroup.ConvertContactGroupChangeRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupFrictionCoefficient` | `(ansys.api.discovery.v0.ChangeDoubleRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupStiffnessFactor` | `(ansys.api.discovery.v0.ChangeDoubleRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupDetectionRadiusFactor` | `(ansys.api.discovery.v0.ChangeDoubleRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupOffset` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupShearStrength` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupTensileStrength` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupAreStrengthLimitsSet` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupAdjustGapOrOverlap` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupMakeJustTouching` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupIdealize` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupDetectionDistanceLow` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupDetectionDistanceHigh` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupSpecifyThermalConductance` | `(ansys.api.discovery.v0.ChangeSpecifyConductanceRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupSpecifyElectricConductance` | `(ansys.api.discovery.v0.ChangeSpecifyConductanceRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupConductanceThickness` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupConductanceMaterial` | `(ansys.api.discovery.v0.ChangeAssignmentRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupThermalContactConductivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupElectricContactConductivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupThermalContactConductance` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ChangeContactGroupElectricContactConductance` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `GetByLabel` | `(ansys.api.discovery.v0.conditions.GetByLabelRequest) -> ansys.api.discovery.v0.connections.contactgroup.ContactGroupDefinition [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.connections.fluidinterface_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FluidInterface` | `ChangeFluidInterfaceType` | `(ansys.api.discovery.v0.connections.fluidinterface.ChangeFluidInterfaceTypeRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceFaceGroupingMethod` | `(ansys.api.discovery.v0.connections.fluidinterface.ChangeFluidInterfaceFaceGroupingMethodRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceConductanceMethod` | `(ansys.api.discovery.v0.ChangeSpecifyConductanceRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceThermalMaterialAssignment` | `(ansys.api.discovery.v0.ChangeAssignmentRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceThermalConductance` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceThermalConductivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceThermalThickness` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceDetectionDistanceHigh` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFluidInterfaceFaceOverlapAllowance` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFSInterfaceInternalRadiationInputEnabled` | `(ansys.api.discovery.v0.ChangeBooleanRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `ChangeFSInterfaceInternalEmissivity` | `(ansys.api.discovery.v0.ChangeQuantityRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.connections.joint_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Joint` | `CreateJoint` | `(ansys.api.discovery.v0.connections.joint.JointCreationRequest) -> ansys.api.discovery.v0.connections.joint.JointCreationResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `ChangeJointSide1Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `ChangeJointSide2Location` | `(ansys.api.discovery.v0.ChangeLocationRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `ChangeJointType` | `(ansys.api.discovery.v0.connections.joint.ChangeJointTypeRequest) -> ansys.api.discovery.v0.ChangeResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.definedvariationstable_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DefinedVariationsTable` | `GetVariation` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.discovery.v0.Variation [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetAllVariations` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.GetAllVariationsResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetAllInputs` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.GetAllInputsResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetAllOutputs` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.GetAllOutputsResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetInputForVariation` | `(ansys.api.discovery.v0.definedvariationstable.GetInputForVariationRequest) -> ansys.api.discovery.v0.InputParameter [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `SetInputValue` | `(ansys.api.discovery.v0.definedvariationstable.SetInputValueRequest) -> ansys.api.discovery.v0.InputParameter [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `CreateVariation` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.Variation [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetOutputForVariation` | `(ansys.api.discovery.v0.definedvariationstable.GetOutputForVariationRequest) -> ansys.api.discovery.v0.OutputParameter [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetInputColumn` | `(ansys.api.discovery.v0.definedvariationstable.GetInputColumnRequest) -> ansys.api.discovery.v0.definedvariationstable.GetInputColumnResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetOutputColumn` | `(ansys.api.discovery.v0.definedvariationstable.GetOutputColumnRequest) -> ansys.api.discovery.v0.definedvariationstable.GetOutputColumnResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `GetCurrentVariation` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.GetCurrentVariationResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `SetCurrentVariation` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.discovery.v0.MessageResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `SetStarredStatus` | `(ansys.api.discovery.v0.definedvariationstable.SetStarredStatusRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `UpdateCurrent` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.UpdateResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `UpdateStarred` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.UpdateResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `UpdateAll` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.UpdateResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariationsTable` | `IsSolving` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.definedvariationstable.IsSolvingResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.engineeringdata.boltdata_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BoltData` | `GetBoltDataFromLibrary` | `(ansys.api.discovery.v0.engineeringdata.boltdata.BoltDataLibraryRequest) -> ansys.api.discovery.v0.engineeringdata.boltdata.BoltDataCreationResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.engineeringdata.fandata_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FanData` | `CreateFan` | `(ansys.api.discovery.v0.engineeringdata.fandata.FanCreationRequest) -> ansys.api.discovery.v0.engineeringdata.fandata.FanCreationResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.historytrackparameters_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `HistoryTrackParameters` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.discovery.v0.HistoryTrackParameter [client_streaming=False, server_streaming=False]` |
| `HistoryTrackParameters` | `GetAll` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.historytrackparameters.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrackParameters` | `Update` | `(ansys.api.discovery.v0.historytrackparameters.UpdateRequest) -> ansys.api.discovery.v0.HistoryTrackParameter [client_streaming=False, server_streaming=False]` |
| `HistoryTrackParameters` | `Replay` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.historytrackparameters.ReplayResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrackParameters` | `GetRecordingStatus` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.historytrackparameters.GetRecordingStatusResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrackParameters` | `SetRecordingStatus` | `(ansys.api.discovery.v0.historytrackparameters.SetRecordingStatusRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.messaging_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Messaging` | `GetMessages` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.messaging.MessagingResponse [client_streaming=False, server_streaming=True]` |
| `Messaging` | `ClearMessages` | `(google.protobuf.Empty) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.monitors_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Monitors` | `CreateMonitor` | `(ansys.api.discovery.v0.monitors.CreateMonitorRequest) -> ansys.api.discovery.v0.monitors.MonitorCreationResponse [client_streaming=False, server_streaming=False]` |
| `Monitors` | `GetAllMonitors` | `(ansys.api.discovery.v0.monitors.GetAllMonitorsRequest) -> ansys.api.discovery.v0.monitors.GetAllMonitorsResponse [client_streaming=False, server_streaming=False]` |
| `Monitors` | `GetMonitorValues` | `(ansys.api.discovery.v0.monitors.GetMonitorValuesRequest) -> ansys.api.discovery.v0.monitors.GetMonitorValuesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.scriptparameters_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `ScriptParameters` | `Get` | `(ansys.api.dbu.v0.EntityIdentifier) -> ansys.api.discovery.v0.ScriptParameter [client_streaming=False, server_streaming=False]` |
| `ScriptParameters` | `GetAll` | `(ansys.api.discovery.v0.scriptparameters.GetAllRequest) -> ansys.api.discovery.v0.scriptparameters.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `ScriptParameters` | `Update` | `(ansys.api.discovery.v0.scriptparameters.UpdateRequest) -> ansys.api.discovery.v0.ScriptParameter [client_streaming=False, server_streaming=False]` |
| `ScriptParameters` | `Replay` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.scriptparameters.ReplayResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.simulations_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Simulations` | `CreateSimulation` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.Simulation [client_streaming=False, server_streaming=False]` |
| `Simulations` | `GetAll` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.simulations.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.solution_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Solution` | `GetSolverFidelity` | `(ansys.api.discovery.v0.solution.SimulationStageRequest) -> ansys.api.discovery.v0.solution.SolverFidelityResponse [client_streaming=False, server_streaming=False]` |
| `Solution` | `SetSolverFidelity` | `(ansys.api.discovery.v0.solution.SolverFidelityRequest) -> google.protobuf.Empty [client_streaming=False, server_streaming=False]` |
| `Solution` | `Solve` | `(ansys.api.discovery.v0.solution.SolveExecutionRequest) -> ansys.api.discovery.v0.solution.SolveExecutionResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v0.unsupported_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Unsupported` | `ExportResultsToOpenVDBMemory` | `(ansys.api.discovery.v0.unsupported.VariableExportRequest) -> ansys.api.discovery.v0.unsupported.ByteArrayResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `ExportResultsToOpenVDBFile` | `(ansys.api.discovery.v0.unsupported.VariableExportRequestToFile) -> ansys.api.dbu.v0.RequestResult [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetLegendMaximumValue` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.unsupported.DoubleValueResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetLegendMinimumValue` | `(google.protobuf.Empty) -> ansys.api.discovery.v0.unsupported.DoubleValueResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `CreateFacetedBodies` | `(ansys.api.discovery.v0.unsupported.CreateFacetedBodiesRequest) -> ansys.api.discovery.v0.unsupported.CreateFacetedBodiesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.commands.application_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Application` | `IsStarted` | `(ansys.api.discovery.v1.commands.application.ApplicationStartedRequest) -> ansys.api.discovery.v1.commands.application.ApplicationStartedResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `Close` | `(ansys.api.discovery.v1.commands.application.CloseApplicationRequest) -> ansys.api.discovery.v1.commands.application.CloseApplicationResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `DisposeTracker` | `(ansys.api.discovery.v1.commands.application.DisposeTrackerRequest) -> ansys.api.discovery.v1.commands.application.DisposeTrackerResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `GetMonikersCompressionMethod` | `(ansys.api.discovery.v1.commands.application.GetMonikerCompressionMethodRequest) -> ansys.api.discovery.v1.commands.application.GetMonikerCompressionMethodResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `GetTracker` | `(ansys.api.discovery.v1.commands.application.GetTrackerRequest) -> ansys.api.discovery.v1.commands.application.GetTrackerResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `GetTrackerChanges` | `(ansys.api.discovery.v1.commands.application.GetTrackerChangesRequest) -> ansys.api.discovery.v1.commands.application.GetTrackerChangesResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `SetAutomaticTrackingState` | `(ansys.api.discovery.v1.commands.application.SetAutomaticTrackingStateRequest) -> ansys.api.discovery.v1.commands.application.SetAutomaticTrackingStateResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `SetMonikersCompressionMethod` | `(ansys.api.discovery.v1.commands.application.SetMonikerCompressionMethodRequest) -> ansys.api.discovery.v1.commands.application.SetMonikerCompressionMethodResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `SetTitle` | `(ansys.api.discovery.v1.commands.application.SetApplicationTitleRequest) -> ansys.api.discovery.v1.commands.application.SetApplicationTitleResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `GetBackend` | `(ansys.api.discovery.v1.commands.application.GetBackendRequest) -> ansys.api.discovery.v1.commands.application.GetBackendResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `Undo` | `(ansys.api.discovery.v1.commands.application.UndoRequest) -> ansys.api.discovery.v1.commands.application.UndoResponse [client_streaming=False, server_streaming=False]` |
| `Application` | `Redo` | `(ansys.api.discovery.v1.commands.application.RedoRequest) -> ansys.api.discovery.v1.commands.application.RedoResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.commands.communication_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Communication` | `Health` | `(ansys.api.discovery.v1.commands.communication.HealthRequest) -> ansys.api.discovery.v1.commands.communication.HealthResponse [client_streaming=False, server_streaming=False]` |
| `Communication` | `Shutdown` | `(ansys.api.discovery.v1.commands.communication.ShutdownRequest) -> ansys.api.discovery.v1.commands.communication.ShutdownResponse [client_streaming=False, server_streaming=False]` |
| `Communication` | `StatusInfo` | `(ansys.api.discovery.v1.commands.communication.StatusInfoRequest) -> ansys.api.discovery.v1.commands.communication.StatusInfoResponse [client_streaming=False, server_streaming=False]` |
| `Communication` | `GetLogs` | `(ansys.api.discovery.v1.commands.communication.LogsRequest) -> ansys.api.discovery.v1.commands.communication.LogsResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.discovery.v1.commands.file_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `File` | `Close` | `(ansys.api.discovery.v1.commands.file.CloseRequest) -> ansys.api.discovery.v1.commands.file.CloseResponse [client_streaming=False, server_streaming=False]` |
| `File` | `GetReferencedDocuments` | `(ansys.api.discovery.v1.commands.file.GetReferencedDocumentsRequest) -> ansys.api.discovery.v1.commands.file.GetReferencedDocumentsResponse [client_streaming=False, server_streaming=True]` |
| `File` | `New` | `(ansys.api.discovery.v1.commands.file.NewRequest) -> ansys.api.discovery.v1.commands.file.NewResponse [client_streaming=False, server_streaming=False]` |
| `File` | `Open` | `(ansys.api.discovery.v1.commands.file.OpenRequest) -> ansys.api.discovery.v1.commands.file.OpenResponse [client_streaming=True, server_streaming=False]` |
| `File` | `OpenFromUrl` | `(ansys.api.discovery.v1.commands.file.OpenFromUrlRequest) -> ansys.api.discovery.v1.commands.file.OpenFromUrlResponse [client_streaming=False, server_streaming=False]` |
| `File` | `Save` | `(ansys.api.discovery.v1.commands.file.SaveRequest) -> ansys.api.discovery.v1.commands.file.SaveResponse [client_streaming=False, server_streaming=True]` |
| `File` | `SaveToUrl` | `(ansys.api.discovery.v1.commands.file.SaveToUrlRequest) -> ansys.api.discovery.v1.commands.file.SaveToUrlResponse [client_streaming=False, server_streaming=False]` |
| `File` | `LoadAddin` | `(ansys.api.discovery.v1.commands.file.LoadAddinRequest) -> ansys.api.discovery.v1.commands.file.LoadAddinResponse [client_streaming=True, server_streaming=False]` |
| `File` | `RunAddinMethod` | `(ansys.api.discovery.v1.commands.file.RunAddinMethodRequest) -> ansys.api.discovery.v1.commands.file.RunAddinMethodResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.commands.historytrack_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `HistoryTrack` | `GetRecordingStatus` | `(ansys.api.discovery.v1.commands.historytrack.GetRecordingStatusRequest) -> ansys.api.discovery.v1.commands.historytrack.GetRecordingStatusResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrack` | `Replay` | `(ansys.api.discovery.v1.commands.historytrack.ReplayRequest) -> ansys.api.discovery.v1.commands.historytrack.ReplayResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrack` | `SetRecordingStatus` | `(ansys.api.discovery.v1.commands.historytrack.SetRecordingStatusRequest) -> ansys.api.discovery.v1.commands.historytrack.SetRecordingStatusResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.commands.message_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Message` | `GetStream` | `(ansys.api.discovery.v1.commands.message.GetMessageRequest) -> ansys.api.discovery.v1.commands.message.MessageResponse [client_streaming=False, server_streaming=True]` |
| `Message` | `Clear` | `(ansys.api.discovery.v1.commands.message.ClearRequest) -> ansys.api.discovery.v1.commands.message.ClearResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.commands.script_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Script` | `RunScriptFile` | `(ansys.api.discovery.v1.commands.script.RunScriptFileRequest) -> ansys.api.discovery.v1.commands.script.RunScriptFileResponse [client_streaming=True, server_streaming=False]` |
| `Script` | `RunScriptFileDebug` | `(ansys.api.discovery.v1.commands.script.RunScriptFileRequest) -> ansys.api.discovery.v1.commands.script.RunScriptFileResponse [client_streaming=True, server_streaming=False]` |
| `Script` | `RunNotTrackedScriptFile` | `(ansys.api.discovery.v1.commands.script.RunScriptFileRequest) -> ansys.api.discovery.v1.commands.script.RunScriptFileResponse [client_streaming=True, server_streaming=False]` |
| `Script` | `RunNotTrackedScriptFileDebug` | `(ansys.api.discovery.v1.commands.script.RunScriptFileRequest) -> ansys.api.discovery.v1.commands.script.RunScriptFileResponse [client_streaming=True, server_streaming=False]` |
| `Script` | `RunScript` | `(ansys.api.discovery.v1.commands.script.RunScriptRequest) -> ansys.api.discovery.v1.commands.script.RunScriptResponse [client_streaming=False, server_streaming=False]` |
| `Script` | `Replay` | `(ansys.api.discovery.v1.commands.script.ReplayRequest) -> ansys.api.discovery.v1.commands.script.ReplayResponse [client_streaming=False, server_streaming=False]` |
| `Script` | `SubscribeToRecording` | `(ansys.api.discovery.v1.commands.script.SubscribeToRecordingRequest) -> ansys.api.discovery.v1.commands.script.RecordingEventResponse [client_streaming=False, server_streaming=True]` |

### `ansys.api.discovery.v1.commands.unsupported_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Unsupported` | `ExportResultsToOpenVDBFile` | `(ansys.api.discovery.v1.commands.unsupported.ExportResultsToOpenVDBFileRequest) -> ansys.api.discovery.v1.commands.unsupported.ExportResultsToOpenVDBFileResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `ExportResultsToOpenVDBMemory` | `(ansys.api.discovery.v1.commands.unsupported.ExportResultsToOpenVDBMemoryRequest) -> ansys.api.discovery.v1.commands.unsupported.ExportResultsToOpenVDBMemoryResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetFacetedBodies` | `(ansys.api.discovery.v1.commands.unsupported.GetFacetedBodiesRequest) -> ansys.api.discovery.v1.commands.unsupported.GetFacetedBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetFacetedBodiesStream` | `(ansys.api.discovery.v1.commands.unsupported.GetFacetedBodiesRequest) -> ansys.api.discovery.v1.commands.unsupported.GetFacetedBodiesResponse [client_streaming=False, server_streaming=True]` |
| `Unsupported` | `CreateFacetedBodies` | `(ansys.api.discovery.v1.commands.unsupported.CreateFacetedBodiesRequest) -> ansys.api.discovery.v1.commands.unsupported.CreateFacetedBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetImportIdMap` | `(ansys.api.discovery.v1.commands.unsupported.GetImportIdMapRequest) -> ansys.api.discovery.v1.commands.unsupported.GetImportIdMapResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `SetExportId` | `(ansys.api.discovery.v1.commands.unsupported.SetExportIdRequest) -> ansys.api.discovery.v1.commands.unsupported.SetExportIdResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetLegendMaximumValue` | `(ansys.api.discovery.v1.commands.unsupported.GetLegendMaximumValueRequest) -> ansys.api.discovery.v1.commands.unsupported.GetLegendMaximumValueResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetLegendMinimumValue` | `(ansys.api.discovery.v1.commands.unsupported.GetLegendMinimumValueRequest) -> ansys.api.discovery.v1.commands.unsupported.GetLegendMinimumValueResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetSimulationContext` | `(ansys.api.discovery.v1.commands.unsupported.GetSimulationContextRequest) -> ansys.api.discovery.v1.commands.unsupported.GetSimulationContextResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `GetSerializedSimulationObjects` | `(ansys.api.discovery.v1.commands.unsupported.GetSerializedSimulationObjectsRequest) -> ansys.api.discovery.v1.commands.unsupported.GetSerializedSimulationObjectsResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `HasActiveSelection` | `(ansys.api.discovery.v1.commands.unsupported.HasActiveSelectionRequest) -> ansys.api.discovery.v1.commands.unsupported.HasActiveSelectionResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `SetSoundEnabled` | `(ansys.api.discovery.v1.commands.unsupported.SoundEnabledRequest) -> ansys.api.discovery.v1.commands.unsupported.SetSoundEnabledResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `RunCommand` | `(ansys.api.discovery.v1.commands.unsupported.RunCommandRequest) -> ansys.api.discovery.v1.commands.unsupported.RunCommandResponse [client_streaming=False, server_streaming=False]` |
| `Unsupported` | `ConvertToHeavyweight` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.commands.unsupported.ConvertToHeavyweightResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.commands.view_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `View` | `GetImage` | `(ansys.api.discovery.v1.commands.view.GetImageRequest) -> ansys.api.discovery.v1.commands.view.GetImageResponse [client_streaming=False, server_streaming=False]` |
| `View` | `Set` | `(ansys.api.discovery.v1.commands.view.SetViewRequest) -> ansys.api.discovery.v1.commands.view.SetViewResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.constructs.coordinatesystem_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `CoordinateSystem` | `Create` | `(ansys.api.discovery.v1.design.constructs.coordinatesystem.CreateRequest) -> ansys.api.discovery.v1.design.constructs.coordinatesystem.CreateResponse [client_streaming=False, server_streaming=False]` |
| `CoordinateSystem` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `CoordinateSystem` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.constructs.coordinatesystem.GetResponse [client_streaming=False, server_streaming=False]` |
| `CoordinateSystem` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.constructs.coordinatesystem.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `CoordinateSystem` | `SetSuppressed` | `(ansys.api.discovery.v1.design.constructs.coordinatesystem.SetSuppressedRequest) -> ansys.api.discovery.v1.design.constructs.coordinatesystem.SetSuppressedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.constructs.datumline_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DatumLine` | `Create` | `(ansys.api.discovery.v1.design.constructs.datumline.DatumLineCreationRequest) -> ansys.api.discovery.v1.design.constructs.datumline.DatumLineCreationResponse [client_streaming=False, server_streaming=False]` |
| `DatumLine` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `DatumLine` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.constructs.datumline.GetResponse [client_streaming=False, server_streaming=False]` |
| `DatumLine` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.constructs.datumline.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DatumLine` | `GetIsDeleted` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetIsDeletedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.constructs.datumplane_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DatumPlane` | `Create` | `(ansys.api.discovery.v1.design.constructs.datumplane.DatumPlaneCreationRequest) -> ansys.api.discovery.v1.design.constructs.datumplane.DatumPlaneCreationResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlane` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlane` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.constructs.datumplane.GetResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlane` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.constructs.datumplane.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlane` | `GetIsDeleted` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetIsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlane` | `GetUpdateState` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetUpdateStateResponse [client_streaming=False, server_streaming=False]` |
| `DatumPlane` | `SetSuppressed` | `(ansys.api.discovery.v1.design.constructs.datumplane.SetSuppressedRequest) -> ansys.api.discovery.v1.design.constructs.datumplane.SetSuppressedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.constructs.datumpoint_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DatumPoint` | `Create` | `(ansys.api.discovery.v1.design.constructs.datumpoint.DatumPointCreationRequest) -> ansys.api.discovery.v1.design.constructs.datumpoint.DatumPointCreationResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.constructs.datumpoint.GetResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.constructs.datumpoint.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `GetIsDeleted` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetIsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `GetIsPinned` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.GetBooleanResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `GetPointPosition` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.constructs.datumpoint.GetPointResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `GetIsSuppressed` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.GetBooleanResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `SetPositionX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `SetPositionY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `SetPositionZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `DatumPoint` | `SetIsSuppressed` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.data.cadmaterial_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `CADMaterial` | `GetAllNames` | `(ansys.api.discovery.v1.design.data.cadmaterial.GetAllNamesRequest) -> ansys.api.discovery.v1.design.data.cadmaterial.GetAllNamesResponse [client_streaming=False, server_streaming=False]` |
| `CADMaterial` | `Create` | `(ansys.api.discovery.v1.design.data.cadmaterial.CreateRequest) -> ansys.api.discovery.v1.design.data.cadmaterial.CreateResponse [client_streaming=False, server_streaming=False]` |
| `CADMaterial` | `Delete` | `(ansys.api.discovery.v1.design.data.cadmaterial.DeleteRequest) -> ansys.api.discovery.v1.design.data.cadmaterial.DeleteResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.designdoc_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DesignDoc` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.designdoc.GetResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `GetActive` | `(ansys.api.discovery.v1.design.designdoc.GetActiveRequest) -> ansys.api.discovery.v1.design.designdoc.GetActiveResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.designdoc.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `GetAsJson` | `(ansys.api.discovery.v1.design.designdoc.GetAsJsonRequest) -> ansys.api.discovery.v1.design.designdoc.GetAsJsonResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `GetAssembly` | `(ansys.api.discovery.v1.design.designdoc.GetAssemblyRequest) -> ansys.api.discovery.v1.design.designdoc.GetAssemblyResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `StreamDesignTessellation` | `(ansys.api.discovery.v1.design.designdoc.DesignTessellationRequest) -> ansys.api.discovery.v1.design.designdoc.DesignTessellationResponse [client_streaming=False, server_streaming=True]` |
| `DesignDoc` | `SetActive` | `(ansys.api.discovery.v1.design.designdoc.SetActiveRequest) -> ansys.api.discovery.v1.design.designdoc.SetActiveResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `GetGeometryUnits` | `(ansys.api.discovery.v1.design.designdoc.GetGeometryUnitsRequest) -> ansys.api.discovery.v1.design.designdoc.GetGeometryUnitsResponse [client_streaming=False, server_streaming=False]` |
| `DesignDoc` | `SetGeometryUnits` | `(ansys.api.discovery.v1.design.designdoc.SetGeometryUnitsRequest) -> ansys.api.discovery.v1.design.designdoc.SetGeometryUnitsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.designentity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DesignEntity` | `SetName` | `(ansys.api.discovery.v1.design.SetDesignEntityNameRequest) -> ansys.api.discovery.v1.design.SetDesignEntityNameResponse [client_streaming=False, server_streaming=False]` |
| `DesignEntity` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.extensions.beam_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Beam` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetBeamProfile` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetOrientationByAngle` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetOrientationByReference` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetIsReversed` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetTreatAs` | `(ansys.api.discovery.v1.design.extensions.beam.SetBeamTreatAsRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetIsRigid` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetAnchorType` | `(ansys.api.discovery.v1.design.extensions.beam.SetBeamAnchorPositionRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetLocationAnchorX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetLocationAnchorY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `SetSuppressed` | `(ansys.api.discovery.v1.design.extensions.beam.SetSuppressedRequest) -> ansys.api.discovery.v1.design.extensions.beam.SetSuppressedResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.extensions.beam.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.extensions.beam.GetResponse [client_streaming=False, server_streaming=False]` |
| `Beam` | `Rotate90Clockwise` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.extensions.bolt_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Bolt` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Bolt` | `SetBolt` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Bolt` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.extensions.bolt.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Bolt` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.extensions.bolt.GetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.extensions.weld_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Weld` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Weld` | `SetWeld` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.design.TrackedSetResponse [client_streaming=False, server_streaming=False]` |
| `Weld` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.extensions.weld.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Weld` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.extensions.weld.GetResponse [client_streaming=False, server_streaming=False]` |
| `Weld` | `GetAllFilletWelds` | `(ansys.api.discovery.v1.design.extensions.weld.GetAllFilletWeldsRequest) -> ansys.api.discovery.v1.design.extensions.weld.GetAllFilletWeldsResponse [client_streaming=False, server_streaming=False]` |
| `Weld` | `GetAllSpotWelds` | `(ansys.api.discovery.v1.design.extensions.weld.GetAllSpotWeldsRequest) -> ansys.api.discovery.v1.design.extensions.weld.GetAllSpotWeldsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.body_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Body` | `CopyFaces` | `(ansys.api.discovery.v1.design.geometry.body.CopyFacesRequest) -> ansys.api.discovery.v1.design.geometry.body.CopyFacesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateBlockBody` | `(ansys.api.discovery.v1.design.geometry.body.CreateBlockBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateBlockBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateDuplicate` | `(ansys.api.discovery.v1.design.geometry.body.CreateDuplicateBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateDuplicateBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateFromLoftWithGuides` | `(ansys.api.discovery.v1.design.geometry.body.CreateBodyFromLoftWithGuidesRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateBodyFromLoftWithGuidesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateFromFace` | `(ansys.api.discovery.v1.design.geometry.body.CreateBodyFromFaceRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateBodyFromFaceResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateExtrudedBody` | `(ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateExtrudedBodyFromFaceProfile` | `(ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyFromFaceProfileRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyFromFaceProfileResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateExtrudedBodyFromLoftProfiles` | `(ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyFromLoftProfilesRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyFromLoftProfilesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreatePlanarBody` | `(ansys.api.discovery.v1.design.geometry.body.CreatePlanarBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.CreatePlanarBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateSphereBody` | `(ansys.api.discovery.v1.design.geometry.body.CreateSphereBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateSphereBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateSurfaceBody` | `(ansys.api.discovery.v1.design.geometry.body.CreateSurfaceBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateSurfaceBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateSurfaceBodyFromTrimmedCurves` | `(ansys.api.discovery.v1.design.geometry.body.CreateSurfaceBodyFromTrimmedCurvesRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateSurfaceBodyFromTrimmedCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateSweepingChain` | `(ansys.api.discovery.v1.design.geometry.body.CreateSweepingChainRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateSweepingChainResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateSweepingProfile` | `(ansys.api.discovery.v1.design.geometry.body.CreateSweepingProfileRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateSweepingProfileResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `CreateTorus` | `(ansys.api.discovery.v1.design.geometry.body.CreateTorusRequest) -> ansys.api.discovery.v1.design.geometry.body.CreateTorusResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `Get` | `(ansys.api.discovery.v1.design.geometry.body.GetBodyRequest) -> ansys.api.discovery.v1.design.geometry.body.GetBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.body.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetAssignedCADMaterial` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetAssignedCADMaterialResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetBoundingBox` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetTightBoundingBox` | `(ansys.api.discovery.v1.design.GetBoundingBoxRequest) -> ansys.api.discovery.v1.design.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetEdges` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetFaces` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetFacesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetName` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetNameResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetUpdateState` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetUpdateStateResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetClosestSeparation` | `(ansys.api.discovery.v1.design.geometry.body.GetClosestSeparationRequest) -> ansys.api.discovery.v1.design.geometry.body.GetClosestSeparationResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetCollision` | `(ansys.api.discovery.v1.design.geometry.body.GetCollisionRequest) -> ansys.api.discovery.v1.design.geometry.body.GetCollisionResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetColor` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetColorResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetFillStyle` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetFillStyleResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetIsEnclosure` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetIsEnclosureBodyResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetIsSuppressed` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetIsSuppressedResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetSurfaceBodyThickness` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetSurfaceBodyThicknessResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetTessellation` | `(ansys.api.discovery.v1.design.geometry.body.GetTessellationRequest) -> ansys.api.discovery.v1.design.geometry.body.GetTessellationResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetTessellationStream` | `(ansys.api.discovery.v1.design.geometry.body.GetTessellationRequest) -> ansys.api.discovery.v1.design.geometry.body.GetTessellationResponse [client_streaming=False, server_streaming=True]` |
| `Body` | `GetVertices` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetVerticesResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetVolume` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.body.GetVolumeResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `GetCentroid` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetCentroidResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `RemoveAssignedCADMaterial` | `(ansys.api.discovery.v1.design.geometry.body.RemoveAssignedCADMaterialRequest) -> ansys.api.discovery.v1.design.geometry.body.RemoveAssignedCADMaterialResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetAssignedCADMaterial` | `(ansys.api.discovery.v1.design.geometry.body.SetAssignedCADMaterialRequest) -> ansys.api.discovery.v1.design.geometry.body.SetAssignedCADMaterialResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetMidSurfaceOffsetType` | `(ansys.api.discovery.v1.design.geometry.body.SetMidSurfaceOffsetTypeRequest) -> ansys.api.discovery.v1.design.geometry.body.SetMidSurfaceOffsetTypeResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetMidSurfaceThickness` | `(ansys.api.discovery.v1.design.geometry.body.SetMidSurfaceThicknessRequest) -> ansys.api.discovery.v1.design.geometry.body.SetMidSurfaceThicknessResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetName` | `(ansys.api.discovery.v1.design.SetDesignEntityNameRequest) -> ansys.api.discovery.v1.design.SetDesignEntityNameResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetColor` | `(ansys.api.discovery.v1.design.SetColorRequest) -> ansys.api.discovery.v1.design.SetColorResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetFillStyle` | `(ansys.api.discovery.v1.design.geometry.body.SetFillStyleRequest) -> ansys.api.discovery.v1.design.geometry.body.SetFillStyleResponse [client_streaming=False, server_streaming=False]` |
| `Body` | `SetSuppressed` | `(ansys.api.discovery.v1.design.geometry.body.SetSuppressedRequest) -> ansys.api.discovery.v1.design.geometry.body.SetSuppressedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.component_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Component` | `Create` | `(ansys.api.discovery.v1.design.geometry.components.CreateRequest) -> ansys.api.discovery.v1.design.geometry.components.CreateResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.geometry.components.GetResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.components.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetBeamBodies` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.components.GetBeamBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetBodies` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.components.GetBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetName` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.components.GetComponentNameResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetPart` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.components.GetPartResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetRootComponent` | `(ansys.api.discovery.v1.design.geometry.components.GetRootComponentRequest) -> ansys.api.discovery.v1.design.geometry.components.GetRootComponentResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `GetUpdateState` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetUpdateStateResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `SetName` | `(ansys.api.discovery.v1.design.SetDesignEntityNameRequest) -> ansys.api.discovery.v1.design.SetDesignEntityNameResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `MakeIndependent` | `(ansys.api.discovery.v1.design.geometry.components.MakeIndependentRequest) -> ansys.api.discovery.v1.design.geometry.components.MakeIndependentResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `ImportGroups` | `(ansys.api.discovery.v1.design.geometry.components.ImportGroupsRequest) -> ansys.api.discovery.v1.design.geometry.components.ImportGroupsResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `SetPlacement` | `(ansys.api.discovery.v1.design.geometry.components.SetPlacementRequest) -> ansys.api.discovery.v1.design.geometry.components.SetPlacementResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `MoveBodiesToComponent` | `(ansys.api.discovery.v1.design.geometry.components.MoveBodiesToComponentRequest) -> ansys.api.discovery.v1.design.geometry.components.MoveBodiesToComponentResponse [client_streaming=False, server_streaming=False]` |
| `Component` | `SetSharedTopology` | `(ansys.api.discovery.v1.design.geometry.components.SetSharedTopologyRequest) -> ansys.api.discovery.v1.design.geometry.components.SetSharedTopologyResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.curve_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Curve` | `CreateFromProfile` | `(ansys.api.discovery.v1.design.geometry.curves.CreateCurvesFromProfileRequest) -> ansys.api.discovery.v1.design.geometry.curves.CreateCurvesFromProfileResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `CreateDesignPoints` | `(ansys.api.discovery.v1.design.geometry.curves.CreateDesignPointsRequest) -> ansys.api.discovery.v1.design.geometry.curves.CreateDesignPointsResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.geometry.curves.GetResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.curves.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `EvaluateNurbsCurve` | `(ansys.api.discovery.v1.design.geometry.curves.EvaluateNurbsCurveRequest) -> ansys.api.discovery.v1.design.geometry.curves.EvaluateNurbsCurveResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `GetInterval` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.curves.GetIntervalResponse [client_streaming=False, server_streaming=False]` |
| `Curve` | `SetSuppressed` | `(ansys.api.discovery.v1.design.geometry.curves.SetSuppressedRequest) -> ansys.api.discovery.v1.design.geometry.curves.SetSuppressedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.edge_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Edge` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.TrackedDeleteResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetBoundingBox` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetTightBoundingBox` | `(ansys.api.discovery.v1.design.GetBoundingBoxRequest) -> ansys.api.discovery.v1.design.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetCurve` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetCurveResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetFaces` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetInterval` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetIntervalResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetIsDeleted` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetIsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetLength` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetLengthResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetStartAndEndPoints` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetStartAndEndPointsResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetUpdateState` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetUpdateStateResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetVertices` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.edges.GetVerticesResponse [client_streaming=False, server_streaming=False]` |
| `Edge` | `GetCentroid` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetCentroidResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.face_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Face` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.geometry.face.GetResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.face.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetArea` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetAreaResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetBoundingBox` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetTightBoundingBox` | `(ansys.api.discovery.v1.design.GetBoundingBoxRequest) -> ansys.api.discovery.v1.design.GetBoundingBoxResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetBoxUV` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetBoxUVResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetClosestSeparation` | `(ansys.api.discovery.v1.design.geometry.face.GetClosestSeparationRequest) -> ansys.api.discovery.v1.design.geometry.face.GetClosestSeparationResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetColor` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetColorResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetEdges` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetExternalEdges` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetExternalEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetFacesByAreaRange` | `(ansys.api.discovery.v1.design.geometry.face.GetFacesByAreaRangeRequest) -> ansys.api.discovery.v1.design.geometry.face.GetFacesByAreaRangeResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetInternalEdges` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetInternalEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetIsDeleted` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetIsDeletedResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetLoops` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetLoopsResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetNormal` | `(ansys.api.discovery.v1.design.geometry.face.GetNormalRequest) -> ansys.api.discovery.v1.design.geometry.face.GetNormalResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetRoundInfo` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetRoundInfoResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetSurface` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetSurfaceResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetUpdateState` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetUpdateStateResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetVertices` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.face.GetVerticesResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `GetCentroid` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.GetCentroidResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `SetColor` | `(ansys.api.discovery.v1.design.SetColorRequest) -> ansys.api.discovery.v1.design.SetColorResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `SetMidSurfaceOffsetType` | `(ansys.api.discovery.v1.design.geometry.face.SetMidSurfaceOffsetTypeRequest) -> ansys.api.discovery.v1.design.geometry.face.SetMidSurfaceOffsetTypeResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `SetMidSurfaceThickness` | `(ansys.api.discovery.v1.design.geometry.face.SetMidSurfaceThicknessRequest) -> ansys.api.discovery.v1.design.geometry.face.SetMidSurfaceThicknessResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `Remove` | `(ansys.api.discovery.v1.design.geometry.face.RemoveFacesRequest) -> ansys.api.discovery.v1.design.geometry.face.RemoveFacesResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `Replace` | `(ansys.api.discovery.v1.design.geometry.face.ReplaceFaceRequest) -> ansys.api.discovery.v1.design.geometry.face.ReplaceFaceResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `Detach` | `(ansys.api.discovery.v1.design.geometry.face.DetachFacesRequest) -> ansys.api.discovery.v1.design.geometry.face.DetachFacesResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `Evaluate` | `(ansys.api.discovery.v1.design.geometry.face.EvaluateRequest) -> ansys.api.discovery.v1.design.geometry.face.EvaluateResponse [client_streaming=False, server_streaming=False]` |
| `Face` | `CreateIsoParamCurves` | `(ansys.api.discovery.v1.design.geometry.face.CreateIsoParamCurvesRequest) -> ansys.api.discovery.v1.design.geometry.face.CreateIsoParamCurvesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.mesh_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Mesh` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.geometry.meshes.GetResponse [client_streaming=False, server_streaming=False]` |
| `Mesh` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.meshes.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Mesh` | `SetSuppressed` | `(ansys.api.discovery.v1.design.geometry.meshes.SetSuppressedRequest) -> ansys.api.discovery.v1.design.geometry.meshes.SetSuppressedResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.geometry.part_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Part` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.geometry.part.GetResponse [client_streaming=False, server_streaming=False]` |
| `Part` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.geometry.part.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Part` | `GetBeams` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.geometry.part.GetBeamsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.parameters.drivingdimension_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DrivingDimension` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.parameters.drivingdimension.GetResponse [client_streaming=False, server_streaming=False]` |
| `DrivingDimension` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.parameters.drivingdimension.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DrivingDimension` | `Set` | `(ansys.api.discovery.v1.design.parameters.drivingdimension.SetDrivingDimensionRequest) -> ansys.api.discovery.v1.design.parameters.drivingdimension.SetDrivingDimensionResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.parameters.historytrack_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `HistoryTrack` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.parameters.historytrack.GetResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrack` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.parameters.historytrack.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `HistoryTrack` | `Set` | `(ansys.api.discovery.v1.design.parameters.historytrack.SetHistoryTrackRequest) -> ansys.api.discovery.v1.design.parameters.historytrack.SetHistoryTrackResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.parameters.script_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Script` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.parameters.script.GetResponse [client_streaming=False, server_streaming=False]` |
| `Script` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.parameters.script.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `Script` | `Set` | `(ansys.api.discovery.v1.design.parameters.script.SetScriptParameterRequest) -> ansys.api.discovery.v1.design.parameters.script.SetScriptParameterResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.relationships.assemblycondition_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `AssemblyCondition` | `CreateAlign` | `(ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAlignRequest) -> ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAlignResponse [client_streaming=False, server_streaming=False]` |
| `AssemblyCondition` | `CreateAnchor` | `(ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAnchorRequest) -> ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAnchorResponse [client_streaming=False, server_streaming=False]` |
| `AssemblyCondition` | `CreateGear` | `(ansys.api.discovery.v1.design.relationships.assemblycondition.CreateGearRequest) -> ansys.api.discovery.v1.design.relationships.assemblycondition.CreateGearResponse [client_streaming=False, server_streaming=False]` |
| `AssemblyCondition` | `CreateOrient` | `(ansys.api.discovery.v1.design.relationships.assemblycondition.CreateOrientRequest) -> ansys.api.discovery.v1.design.relationships.assemblycondition.CreateOrientResponse [client_streaming=False, server_streaming=False]` |
| `AssemblyCondition` | `CreateRigid` | `(ansys.api.discovery.v1.design.relationships.assemblycondition.CreateRigidRequest) -> ansys.api.discovery.v1.design.relationships.assemblycondition.CreateRigidResponse [client_streaming=False, server_streaming=False]` |
| `AssemblyCondition` | `CreateTangent` | `(ansys.api.discovery.v1.design.relationships.assemblycondition.CreateTangentRequest) -> ansys.api.discovery.v1.design.relationships.assemblycondition.CreateTangentResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.relationships.pattern_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Pattern` | `CreateCircular` | `(ansys.api.discovery.v1.design.relationships.pattern.CircularPatternCreationRequest) -> ansys.api.discovery.v1.design.relationships.pattern.CircularPatternCreationResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `CreateFill` | `(ansys.api.discovery.v1.design.relationships.pattern.FillPatternCreationRequest) -> ansys.api.discovery.v1.design.relationships.pattern.FillPatternCreationResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `CreateLinear` | `(ansys.api.discovery.v1.design.relationships.pattern.LinearPatternCreationRequest) -> ansys.api.discovery.v1.design.relationships.pattern.LinearPatternCreationResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `SetCircularData` | `(ansys.api.discovery.v1.design.relationships.pattern.SetCircularPatternDataRequest) -> ansys.api.discovery.v1.design.relationships.pattern.SetCircularPatternDataResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `SetLinearData` | `(ansys.api.discovery.v1.design.relationships.pattern.SetLinearPatternDataRequest) -> ansys.api.discovery.v1.design.relationships.pattern.SetLinearPatternDataResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `Remove` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.design.relationships.pattern.RemoveResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `RemoveMember` | `(ansys.api.discovery.v1.design.relationships.pattern.RemoveMemberRequest) -> ansys.api.discovery.v1.design.relationships.pattern.RemoveMemberResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `SetPatternValue` | `(ansys.api.discovery.v1.design.relationships.pattern.SetPatternValueRequest) -> ansys.api.discovery.v1.design.relationships.pattern.SetPatternValueResponse [client_streaming=False, server_streaming=False]` |
| `Pattern` | `UpdateFill` | `(ansys.api.discovery.v1.design.relationships.pattern.UpdateFillRequest) -> ansys.api.discovery.v1.design.relationships.pattern.UpdateFillResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.selections.bodyselection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BodySelection` | `GetAllVisibleBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetAllVisibleBodiesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetAllBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetAllBodiesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetAllSurfaceBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetAllSurfaceBodiesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetAllSolidBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetAllSolidBodiesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesFromNamedSelection` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesFromNamedSelectionRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithName` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithNameRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithVolumeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithSurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithSurfaceAreaRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithXLocation` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithYLocation` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithZLocation` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GetBodiesWithColor` | `(ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithColorRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `InvertBodySelection` | `(ansys.api.discovery.v1.design.selections.bodyselection.InvertBodySelectionRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByVolumeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesBySurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceAreaRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxSurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinSurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByFaceCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByIntRangeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxFaceCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinFaceCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByEdgeCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByIntRangeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxEdgeCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinEdgeCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByLoopCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByIntRangeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxLoopCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinLoopCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByNumberSurfaces` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceCountRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByNumberCurves` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveCountRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxNumberSurfaces` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceTypeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMaxNumberCurves` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveTypeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinNumberSurfaces` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceTypeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesMinNumberCurves` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveTypeRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByNumberSurfacesPercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceTypePercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByNumberCurvesPercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveTypePercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByColor` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByColorRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesByName` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByNameRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesContainingSurfaceTypes` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesContainingSurfaceTypesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesContainingCurveTypes` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesContainingCurveTypesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesVolumePercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesPercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesSurfaceAreaPercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesPercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesFaceCountPercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesPercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesEdgeCountPercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesPercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterBodiesLoopCountPercentile` | `(ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesPercentileRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterSurfaceBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `FilterSolidBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendToSameVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendToSameSurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendToSameNumberOfFaces` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendToSameNumberOfEdges` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendToSameColor` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendToSameName` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `ExtendNearbyBodies` | `(ansys.api.discovery.v1.design.selections.bodyselection.ExtendNearbyBodiesRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesByVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesBySurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesByFaceCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesByEdgeCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesByLoopCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesByNumberOfSurfaces` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `OrderBodiesByNumberOfCurves` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesByVolume` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesBySurfaceArea` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesByFaceCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesByEdgeCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesByLoopCount` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesByColor` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |
| `BodySelection` | `GroupBodiesByName` | `(ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequest) -> ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.selections.edgeselection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `EdgeSelection` | `GetAllVisibleEdges` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetAllVisibleEdgesRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GetAllEdges` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetAllEdgesRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GetEdgesFromNamedSelection` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesFromNamedSelectionRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GetEdgesWithLength` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesWithLengthRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GetEdgesWithXLocation` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GetEdgesWithYLocation` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GetEdgesWithZLocation` | `(ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `InvertEdgeSelection` | `(ansys.api.discovery.v1.design.selections.edgeselection.InvertEdgeSelectionRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `FilterEdgesByLength` | `(ansys.api.discovery.v1.design.selections.edgeselection.FilterEdgesByLengthRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `FilterEdgesMaxLength` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `FilterEdgesMinLength` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `FilterEdgesByCurveType` | `(ansys.api.discovery.v1.design.selections.edgeselection.FilterEdgesByCurveTypeRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `FilterEdgesLengthPercentile` | `(ansys.api.discovery.v1.design.selections.edgeselection.FilterEdgesPercentileRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `ExtendNearbyEdges` | `(ansys.api.discovery.v1.design.selections.edgeselection.ExtendNearbyEdgesRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `ExtendToConnected` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `ExtendToTangentChain` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `ExtendToCoaxialEdges` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `OrderEdgesByLength` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `EdgeSelection` | `GroupEdgesByCurveType` | `(ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.edgeselection.EdgeGroupResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.selections.faceselection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FaceSelection` | `GetAllVisibleFaces` | `(ansys.api.discovery.v1.design.selections.faceselection.GetAllVisibleFacesRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetAllFaces` | `(ansys.api.discovery.v1.design.selections.faceselection.GetAllFacesRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetFacesFromNamedSelection` | `(ansys.api.discovery.v1.design.selections.faceselection.GetFacesFromNamedSelectionRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetFacesWithArea` | `(ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithAreaRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetFacesWithXLocation` | `(ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetFacesWithYLocation` | `(ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetFacesWithZLocation` | `(ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithLocationRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GetFacesWithColor` | `(ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithColorRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `InvertFaceSelection` | `(ansys.api.discovery.v1.design.selections.faceselection.InvertFaceSelectionRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByArea` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByAreaRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMaxArea` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMinArea` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByPerimeter` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByPerimeterRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMaxPerimeter` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMinPerimeter` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByEdgeCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByIntRangeRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMaxEdgeCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMinEdgeCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByLoopCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByIntRangeRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMaxLoopCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMinLoopCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByNumberCurves` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveCountRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMaxNumberCurves` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveTypeRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesMinNumberCurves` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveTypeRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesContainingCurveTypes` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesContainingCurveTypesRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByColor` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByColorRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesAreaPercentile` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesPercentileRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesPerimeterPercentile` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesPercentileRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesEdgeCountPercentile` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesPercentileRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesLoopCountPercentile` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesPercentileRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `FilterFacesByNumberCurvesPercentile` | `(ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveTypePercentileRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `ExtendToSameArea` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `ExtendToSameNumberOfEdges` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `ExtendToSameNumberOfLoops` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `ExtendToSameColor` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `ExtendToCoincident` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `ExtendToCoaxialFaces` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `OrderFacesByArea` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `OrderFacesByPerimeter` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `OrderFacesByEdgeCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `OrderFacesByLoopCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `OrderFacesByNumberCurves` | `(ansys.api.discovery.v1.design.selections.faceselection.OrderFacesByCurveTypeRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByArea` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByPerimeter` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByBody` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByEdgeCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByLoopCount` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByColor` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |
| `FaceSelection` | `GroupFacesByCoincident` | `(ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequest) -> ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.design.selections.namedselection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `NamedSelection` | `Create` | `(ansys.api.discovery.v1.design.selections.namedselection.CreateRequest) -> ansys.api.discovery.v1.design.selections.namedselection.CreateResponse [client_streaming=False, server_streaming=False]` |
| `NamedSelection` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `NamedSelection` | `DeleteByName` | `(ansys.api.discovery.v1.design.selections.namedselection.DeleteByNameRequest) -> ansys.api.discovery.v1.design.selections.namedselection.DeleteByNameResponse [client_streaming=False, server_streaming=False]` |
| `NamedSelection` | `Get` | `(ansys.api.discovery.v1.EntityRequest) -> ansys.api.discovery.v1.design.selections.namedselection.GetResponse [client_streaming=False, server_streaming=False]` |
| `NamedSelection` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.design.selections.namedselection.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `NamedSelection` | `SetName` | `(ansys.api.discovery.v1.design.SetDesignEntityNameRequest) -> ansys.api.discovery.v1.design.SetDesignEntityNameResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.engineeringdata.beamprofiledata_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BeamProfileData` | `CreateCircular` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileCircularRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileCircularResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `CreateSegments` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileSegmentsRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileSegmentsResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `CreateDescriptiveSegments` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileSegmentsRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateDescriptiveProfileSegmentsResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `Delete` | `(ansys.api.discovery.v1.MultipleEntitiesRequest) -> ansys.api.discovery.v1.DeleteResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `GetName` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfileNameRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfileNameResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `GetParts` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfilePartsRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfilePartsResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `GetProperties` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfilePropertiesRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfilePropertiesResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `GetCrossSectionInfo` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfileCrossSectionInfoRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfileCrossSectionInfoResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `GetFromLibrary` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.DataLibraryRequest) -> ansys.api.discovery.v1.engineeringdata.beamprofiledata.BeamDataResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `MoveToProject` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.DataLibraryRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `ImportToProject` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.ImportLibraryDataRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `SaveToUserLibrary` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.DataLibraryRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BeamProfileData` | `ChangeQuantityProperty` | `(ansys.api.discovery.v1.engineeringdata.beamprofiledata.ChangeDataQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.engineeringdata.boltdata_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BoltData` | `GetFromLibrary` | `(ansys.api.discovery.v1.engineeringdata.boltdata.BoltDataLibraryRequest) -> ansys.api.discovery.v1.engineeringdata.boltdata.BoltDataCreationResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.engineeringdata.fandata_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FanData` | `Create` | `(ansys.api.discovery.v1.engineeringdata.fandata.FanDataCreationRequest) -> ansys.api.discovery.v1.engineeringdata.fandata.FanDataCreationResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ConvertToUser` | `(ansys.api.discovery.v1.engineeringdata.fandata.FanDataConvertToUserRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `SetName` | `(ansys.api.discovery.v1.SetStringRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `SetSpecification` | `(ansys.api.discovery.v1.engineeringdata.fandata.SetFanDataSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `SetPressureRise` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ChangeVolumeFlowRateAdd` | `(ansys.api.discovery.v1.AddTableQuantityPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ChangeVolumeFlowRateEdit` | `(ansys.api.discovery.v1.EditTableQuantityPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ChangeVolumeFlowRateRemove` | `(ansys.api.discovery.v1.RemoveTableRowRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ChangeVelocityAdd` | `(ansys.api.discovery.v1.AddTableQuantityPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ChangeVelocityEdit` | `(ansys.api.discovery.v1.EditTableQuantityPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanData` | `ChangeVelocityRemove` | `(ansys.api.discovery.v1.RemoveTableRowRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.engineeringdata.material_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Material` | `CreateMaterial` | `(ansys.api.discovery.v1.engineeringdata.material.MaterialCreationRequest) -> ansys.api.discovery.v1.engineeringdata.material.MaterialCreationResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `DuplicateLibraryMaterial` | `(ansys.api.discovery.v1.engineeringdata.material.MaterialDuplicateLibraryRequest) -> ansys.api.discovery.v1.engineeringdata.material.MaterialDuplicateLibraryResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `GetById` | `(ansys.api.discovery.v1.engineeringdata.material.MaterialGetByIdRequest) -> ansys.api.discovery.v1.engineeringdata.material.MaterialGetByIdResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `GetByLabel` | `(ansys.api.discovery.v1.engineeringdata.material.MaterialGetByLabelRequest) -> ansys.api.discovery.v1.engineeringdata.material.MaterialGetByLabelResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeDensity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeViscosity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeTensileYieldStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeTensileUltimateYieldStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeCompressiveYieldStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeCompressiveUltimateYieldStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeMolarMass` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeYoungsModulus` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangePoissonsRatio` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeCoefficientOfThermalExpansion` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeThermalConductivitySpecification` | `(ansys.api.discovery.v1.engineeringdata.material.SetThermalConductivitySpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeIsotropicThermalConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeOrthotropicThermalConductivityX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeOrthotropicThermalConductivityY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeOrthotropicThermalConductivityZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeSpecificHeat` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeRelativePermittivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeElectricConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeElectricLossTangent` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeRelativePermeability` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeMagneticLossTangent` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeEmbodiedEnergy` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeCo2Footprint` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeRecycle` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeAlpha` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeRed` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeGreen` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeBlue` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeMetallicFinish` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeRoughness` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `ChangeLightTransmittance` | `(ansys.api.discovery.v1.SetIntRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `AddMaterialTableRow` | `(ansys.api.discovery.v1.AddTableQuantityPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `EditMaterialTableRow` | `(ansys.api.discovery.v1.EditTableQuantityPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Material` | `RemoveMaterialTableRow` | `(ansys.api.discovery.v1.RemoveTableRowRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.engineeringdata.welddata_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `WeldData` | `GetWeldDataFromLibrary` | `(ansys.api.discovery.v1.engineeringdata.welddata.WeldDataLibraryRequest) -> ansys.api.discovery.v1.engineeringdata.welddata.WeldDataCreationResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.edit_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Edit` | `Boolean` | `(ansys.api.discovery.v1.operations.edit.BooleanRequest) -> ansys.api.discovery.v1.operations.edit.BooleanResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Chamfer` | `(ansys.api.discovery.v1.operations.edit.ChamferRequest) -> ansys.api.discovery.v1.operations.edit.ChamferResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `CombineIntersectBodies` | `(ansys.api.discovery.v1.operations.edit.CombineIntersectBodiesRequest) -> ansys.api.discovery.v1.operations.edit.CombineIntersectBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `CombineMergeBodies` | `(ansys.api.discovery.v1.operations.edit.CombineMergeBodiesRequest) -> ansys.api.discovery.v1.operations.edit.CombineMergeBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `DetachFaces` | `(ansys.api.discovery.v1.operations.edit.DetachFacesRequest) -> ansys.api.discovery.v1.operations.edit.DetachFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `DraftFaces` | `(ansys.api.discovery.v1.operations.edit.DraftFacesRequest) -> ansys.api.discovery.v1.operations.edit.DraftFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ExtrudeEdges` | `(ansys.api.discovery.v1.operations.edit.ExtrudeEdgesRequest) -> ansys.api.discovery.v1.operations.edit.ExtrudeEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ExtrudeEdgesUpTo` | `(ansys.api.discovery.v1.operations.edit.ExtrudeEdgesUpToRequest) -> ansys.api.discovery.v1.operations.edit.ExtrudeEdgesUpToResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ExtrudeFaces` | `(ansys.api.discovery.v1.operations.edit.ExtrudeFacesRequest) -> ansys.api.discovery.v1.operations.edit.ExtrudeFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ExtrudeFacesUpTo` | `(ansys.api.discovery.v1.operations.edit.ExtrudeFacesUpToRequest) -> ansys.api.discovery.v1.operations.edit.ExtrudeFacesUpToResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `FaceOffset` | `(ansys.api.discovery.v1.operations.edit.FaceOffsetRequest) -> ansys.api.discovery.v1.operations.edit.FaceOffsetResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `FillEdgeLoops` | `(ansys.api.discovery.v1.operations.edit.FillEdgeLoopsRequest) -> ansys.api.discovery.v1.operations.edit.FillEdgeLoopsResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Fillet` | `(ansys.api.discovery.v1.operations.edit.FilletRequest) -> ansys.api.discovery.v1.operations.edit.FilletResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `FillFaces` | `(ansys.api.discovery.v1.operations.edit.FillFacesRequest) -> ansys.api.discovery.v1.operations.edit.FillFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `FullFillet` | `(ansys.api.discovery.v1.operations.edit.FullFilletRequest) -> ansys.api.discovery.v1.operations.edit.FullFilletResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ImprintCurves` | `(ansys.api.discovery.v1.operations.edit.ImprintCurvesRequest) -> ansys.api.discovery.v1.operations.edit.ImprintCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ImprintProjectedCurves` | `(ansys.api.discovery.v1.operations.edit.ImprintProjectedCurvesRequest) -> ansys.api.discovery.v1.operations.edit.ImprintProjectedCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `IntersectCurves` | `(ansys.api.discovery.v1.operations.edit.IntersectCurvesRequest) -> ansys.api.discovery.v1.operations.edit.IntersectCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `IntersectCurveAndSurface` | `(ansys.api.discovery.v1.operations.edit.IntersectCurveAndSurfaceRequest) -> ansys.api.discovery.v1.operations.edit.IntersectCurveAndSurfaceResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `MapBody` | `(ansys.api.discovery.v1.operations.edit.MapBodyRequest) -> ansys.api.discovery.v1.operations.edit.MapResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `MergeBodies` | `(ansys.api.discovery.v1.operations.edit.MergeBodiesRequest) -> ansys.api.discovery.v1.operations.edit.MergeBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Mirror` | `(ansys.api.discovery.v1.operations.edit.MirrorRequest) -> ansys.api.discovery.v1.operations.edit.MirrorResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `MoveImprintEdges` | `(ansys.api.discovery.v1.operations.edit.MoveImprintEdgesRequest) -> ansys.api.discovery.v1.operations.edit.MoveImprintEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `MoveRotate` | `(ansys.api.discovery.v1.operations.edit.MoveRotateRequest) -> ansys.api.discovery.v1.operations.edit.MoveRotateResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `MoveTranslate` | `(ansys.api.discovery.v1.operations.edit.MoveTranslateRequest) -> ansys.api.discovery.v1.operations.edit.MoveTranslateResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `OffsetEdges` | `(ansys.api.discovery.v1.operations.edit.OffsetEdgesRequest) -> ansys.api.discovery.v1.operations.edit.OffsetEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `OffsetFaceCurves` | `(ansys.api.discovery.v1.operations.edit.OffsetFaceCurvesRequest) -> ansys.api.discovery.v1.operations.edit.OffsetFaceCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `OffsetFaces` | `(ansys.api.discovery.v1.operations.edit.OffsetFacesRequest) -> ansys.api.discovery.v1.operations.edit.OffsetFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `OffsetFacesSetRadius` | `(ansys.api.discovery.v1.operations.edit.OffsetFacesSetRadiusRequest) -> ansys.api.discovery.v1.operations.edit.OffsetFacesSetRadiusResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ProjectCurves` | `(ansys.api.discovery.v1.operations.edit.ProjectCurvesRequest) -> ansys.api.discovery.v1.operations.edit.ProjectCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ProjectPoint` | `(ansys.api.discovery.v1.operations.edit.ProjectPointRequest) -> ansys.api.discovery.v1.operations.edit.ProjectPointResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ProjectToSolid` | `(ansys.api.discovery.v1.operations.edit.ProjectToSolidRequest) -> ansys.api.discovery.v1.operations.edit.ProjectToSolidResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `PullCurvePoint` | `(ansys.api.discovery.v1.operations.edit.PullCurvePointRequest) -> ansys.api.discovery.v1.operations.edit.PullCurvePointResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `RevolveCurves` | `(ansys.api.discovery.v1.operations.edit.RevolveCurvesRequest) -> ansys.api.discovery.v1.operations.edit.RevolveCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `RevolveFaces` | `(ansys.api.discovery.v1.operations.edit.RevolveFacesRequest) -> ansys.api.discovery.v1.operations.edit.RevolveFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `RevolveFacesByHelix` | `(ansys.api.discovery.v1.operations.edit.RevolveFacesByHelixRequest) -> ansys.api.discovery.v1.operations.edit.RevolveFacesByHelixResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `RevolveFacesUpTo` | `(ansys.api.discovery.v1.operations.edit.RevolveFacesUpToRequest) -> ansys.api.discovery.v1.operations.edit.RevolveFacesUpToResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Rotate` | `(ansys.api.discovery.v1.operations.edit.RotateRequest) -> ansys.api.discovery.v1.operations.edit.RotateResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Scale` | `(ansys.api.discovery.v1.operations.edit.ScaleRequest) -> ansys.api.discovery.v1.operations.edit.ScaleResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ScaleNonUniform` | `(ansys.api.discovery.v1.operations.edit.ScaleNonUniformRequest) -> ansys.api.discovery.v1.operations.edit.ScaleNonUniformResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SeparatePieces` | `(ansys.api.discovery.v1.operations.edit.SeparatePiecesRequest) -> ansys.api.discovery.v1.operations.edit.SeparatePiecesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Shell` | `(ansys.api.discovery.v1.operations.edit.ShellRequest) -> ansys.api.discovery.v1.operations.edit.ShellResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SplitBodies` | `(ansys.api.discovery.v1.operations.edit.SplitBodyRequest) -> ansys.api.discovery.v1.operations.edit.SplitBodyResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SplitEdges` | `(ansys.api.discovery.v1.operations.edit.SplitEdgesRequest) -> ansys.api.discovery.v1.operations.edit.SplitEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SplitFaces` | `(ansys.api.discovery.v1.operations.edit.SplitFaceRequest) -> ansys.api.discovery.v1.operations.edit.SplitFaceResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SweepEdges` | `(ansys.api.discovery.v1.operations.edit.SweepEdgesRequest) -> ansys.api.discovery.v1.operations.edit.SweepEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SweepFaces` | `(ansys.api.discovery.v1.operations.edit.SweepFacesRequest) -> ansys.api.discovery.v1.operations.edit.SweepFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SweepWithGuide` | `(ansys.api.discovery.v1.operations.edit.SweepWithGuideRequest) -> ansys.api.discovery.v1.operations.edit.SweepWithGuideResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `ThickenFaces` | `(ansys.api.discovery.v1.operations.edit.ThickenFacesRequest) -> ansys.api.discovery.v1.operations.edit.ThickenFacesResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `RevolveDatumPoint` | `(ansys.api.discovery.v1.operations.edit.RevolveDatumPointRequest) -> ansys.api.discovery.v1.operations.edit.RevolveDatumPointResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `RevolveDatumPointByHelix` | `(ansys.api.discovery.v1.operations.edit.RevolveDatumPointByHelixRequest) -> ansys.api.discovery.v1.operations.edit.RevolveDatumPointByHelixResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `SweepDatumPoint` | `(ansys.api.discovery.v1.operations.edit.SweepDatumPointRequest) -> ansys.api.discovery.v1.operations.edit.SweepDatumPointResponse [client_streaming=False, server_streaming=False]` |
| `Edit` | `Translate` | `(ansys.api.discovery.v1.operations.edit.TranslateRequest) -> ansys.api.discovery.v1.operations.edit.TranslateResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.facet_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Facet` | `FacetAutoFix` | `(ansys.api.discovery.v1.operations.facet.FacetAutoFixRequest) -> ansys.api.discovery.v1.operations.facet.FacetAutoFixResponse [client_streaming=False, server_streaming=False]` |
| `Facet` | `ShrinkWrapBody` | `(ansys.api.discovery.v1.operations.facet.ShrinkWrapBodyRequest) -> ansys.api.discovery.v1.operations.facet.ShrinkWrapBodyResponse [client_streaming=False, server_streaming=False]` |
| `Facet` | `ShrinkWrapMesh` | `(ansys.api.discovery.v1.operations.facet.ShrinkWrapMeshRequest) -> ansys.api.discovery.v1.operations.facet.ShrinkWrapMeshResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.measure_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Measure` | `MinDistanceBetweenObjects` | `(ansys.api.discovery.v1.operations.measure.MinDistanceBetweenObjectsRequest) -> ansys.api.discovery.v1.operations.measure.MinDistanceBetweenObjectsResponse [client_streaming=False, server_streaming=False]` |
| `Measure` | `MinDistanceBetweenSelectionObjects` | `(ansys.api.discovery.v1.operations.measure.MinDistanceBetweenSelectionObjectsRequest) -> ansys.api.discovery.v1.operations.measure.MinDistanceBetweenSelectionObjectsResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.prepare_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Prepare` | `CreateEnclosureBox` | `(ansys.api.discovery.v1.operations.prepare.CreateEnclosureBoxRequest) -> ansys.api.discovery.v1.operations.prepare.CreateEnclosureResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `CreateEnclosureCylinder` | `(ansys.api.discovery.v1.operations.prepare.CreateEnclosureCylinderRequest) -> ansys.api.discovery.v1.operations.prepare.CreateEnclosureResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `CreateEnclosureSphere` | `(ansys.api.discovery.v1.operations.prepare.CreateEnclosureSphereRequest) -> ansys.api.discovery.v1.operations.prepare.CreateEnclosureResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `DetectSweepableBodies` | `(ansys.api.discovery.v1.operations.prepare.DetectSweepableBodiesRequest) -> ansys.api.discovery.v1.operations.prepare.DetectSweepableBodiesResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `FindHelixes` | `(ansys.api.discovery.v1.operations.prepare.FindHelixesRequest) -> ansys.api.discovery.v1.operations.prepare.FindHelixesResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `FindMappableFaces` | `(ansys.api.discovery.v1.operations.prepare.FindMappableFacesRequest) -> ansys.api.discovery.v1.operations.prepare.FindMappableFacesResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `EnhancedShareTopology` | `(ansys.api.discovery.v1.operations.prepare.ShareTopologyRequest) -> ansys.api.discovery.v1.operations.prepare.EnhancedShareTopologyResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `ExtractVolumeFromEdgeLoops` | `(ansys.api.discovery.v1.operations.prepare.ExtractVolumeFromEdgeLoopsRequest) -> ansys.api.discovery.v1.operations.prepare.ExtractVolumeFromEdgeLoopsResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `ExtractVolumeFromFaces` | `(ansys.api.discovery.v1.operations.prepare.ExtractVolumeFromFacesRequest) -> ansys.api.discovery.v1.operations.prepare.ExtractVolumeFromFacesResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `FindAndRemoveLogos` | `(ansys.api.discovery.v1.operations.prepare.FindAndRemoveLogosRequest) -> ansys.api.discovery.v1.operations.prepare.FindAndRemoveLogosResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `FindLogos` | `(ansys.api.discovery.v1.operations.prepare.FindLogosRequest) -> ansys.api.discovery.v1.operations.prepare.FindLogosResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `RemoveFaces` | `(ansys.api.discovery.v1.operations.prepare.RemoveFacesRequest) -> ansys.api.discovery.v1.operations.prepare.RemoveFacesResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `RemoveLogo` | `(ansys.api.discovery.v1.operations.prepare.RemoveLogoRequest) -> ansys.api.discovery.v1.operations.prepare.RemoveLogoResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `RemoveRounds` | `(ansys.api.discovery.v1.operations.prepare.RemoveRoundsRequest) -> ansys.api.discovery.v1.operations.prepare.RemoveRoundsResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `ShareTopology` | `(ansys.api.discovery.v1.operations.prepare.ShareTopologyRequest) -> ansys.api.discovery.v1.operations.prepare.ShareTopologyResponse [client_streaming=False, server_streaming=False]` |
| `Prepare` | `UnshareTopology` | `(ansys.api.discovery.v1.operations.prepare.UnshareTopologyRequest) -> ansys.api.discovery.v1.operations.prepare.UnshareTopologyResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.rayfire_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `RayFire` | `Fire` | `(ansys.api.discovery.v1.operations.rayfire.FireRequest) -> ansys.api.discovery.v1.operations.rayfire.FireResponse [client_streaming=False, server_streaming=False]` |
| `RayFire` | `FireFaces` | `(ansys.api.discovery.v1.operations.rayfire.FireFacesRequest) -> ansys.api.discovery.v1.operations.rayfire.FireFacesResponse [client_streaming=False, server_streaming=False]` |
| `RayFire` | `FireOrdered` | `(ansys.api.discovery.v1.operations.rayfire.FireOrderedRequest) -> ansys.api.discovery.v1.operations.rayfire.FireOrderedResponse [client_streaming=False, server_streaming=False]` |
| `RayFire` | `FireOrderedUV` | `(ansys.api.discovery.v1.operations.rayfire.FireOrderedUVRequest) -> ansys.api.discovery.v1.operations.rayfire.FireOrderedUVResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.repair_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Repair` | `FindAdjustSimplify` | `(ansys.api.discovery.v1.operations.repair.FindAdjustSimplifyRequest) -> ansys.api.discovery.v1.operations.repair.FindAdjustSimplifyResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindAndFixExtraEdges` | `(ansys.api.discovery.v1.operations.repair.FindAndFixExtraEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindAndFixExtraEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindAndFixShortEdges` | `(ansys.api.discovery.v1.operations.repair.FindAndFixShortEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindAndFixShortEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindAndFixSplitEdges` | `(ansys.api.discovery.v1.operations.repair.FindAndFixSplitEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindAndFixSplitEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindAndFixStitchFaces` | `(ansys.api.discovery.v1.operations.repair.FindAndFixStitchFacesRequest) -> ansys.api.discovery.v1.operations.repair.FindAndFixStitchFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindAndSimplify` | `(ansys.api.discovery.v1.operations.repair.FindAndSimplifyRequest) -> ansys.api.discovery.v1.operations.repair.FindAndSimplifyResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindCurveGaps` | `(ansys.api.discovery.v1.operations.repair.FindCurveGapsRequest) -> ansys.api.discovery.v1.operations.repair.FindCurveGapsResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindDuplicateCurves` | `(ansys.api.discovery.v1.operations.repair.FindDuplicateCurvesRequest) -> ansys.api.discovery.v1.operations.repair.FindDuplicateCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindDuplicateFaces` | `(ansys.api.discovery.v1.operations.repair.FindDuplicateFacesRequest) -> ansys.api.discovery.v1.operations.repair.FindDuplicateFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindExtraEdges` | `(ansys.api.discovery.v1.operations.repair.FindExtraEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindExtraEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindGaps` | `(ansys.api.discovery.v1.operations.repair.FindGapsRequest) -> ansys.api.discovery.v1.operations.repair.FindGapsResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindInexactEdges` | `(ansys.api.discovery.v1.operations.repair.FindInexactEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindInexactEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindInterference` | `(ansys.api.discovery.v1.operations.repair.FindInterferenceRequest) -> ansys.api.discovery.v1.operations.repair.FindInterferenceResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindMissingFaces` | `(ansys.api.discovery.v1.operations.repair.FindMissingFacesRequest) -> ansys.api.discovery.v1.operations.repair.FindMissingFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindShortEdges` | `(ansys.api.discovery.v1.operations.repair.FindShortEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindShortEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindSmallCurves` | `(ansys.api.discovery.v1.operations.repair.FindSmallCurvesRequest) -> ansys.api.discovery.v1.operations.repair.FindSmallCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindSmallFaces` | `(ansys.api.discovery.v1.operations.repair.FindSmallFacesRequest) -> ansys.api.discovery.v1.operations.repair.FindSmallFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindSplitEdges` | `(ansys.api.discovery.v1.operations.repair.FindSplitEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FindSplitEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindStitchFaces` | `(ansys.api.discovery.v1.operations.repair.FindStitchFacesRequest) -> ansys.api.discovery.v1.operations.repair.FindStitchFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FitCurves` | `(ansys.api.discovery.v1.operations.repair.FitCurvesRequest) -> ansys.api.discovery.v1.operations.repair.FitCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixAdjustSimplify` | `(ansys.api.discovery.v1.operations.repair.FixAdjustSimplifyRequest) -> ansys.api.discovery.v1.operations.repair.FixAdjustSimplifyResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixCurveGaps` | `(ansys.api.discovery.v1.operations.repair.FixCurveGapsRequest) -> ansys.api.discovery.v1.operations.repair.FixCurveGapsResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixDuplicateCurves` | `(ansys.api.discovery.v1.operations.repair.FixDuplicateCurvesRequest) -> ansys.api.discovery.v1.operations.repair.FixDuplicateCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixDuplicateFaces` | `(ansys.api.discovery.v1.operations.repair.FixDuplicateFacesRequest) -> ansys.api.discovery.v1.operations.repair.FixDuplicateFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixExtraEdges` | `(ansys.api.discovery.v1.operations.repair.FixExtraEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FixExtraEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixGaps` | `(ansys.api.discovery.v1.operations.repair.FixGapsRequest) -> ansys.api.discovery.v1.operations.repair.FixGapsResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixInexactEdges` | `(ansys.api.discovery.v1.operations.repair.FixInexactEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FixInexactEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixInterference` | `(ansys.api.discovery.v1.operations.repair.FixInterferenceRequest) -> ansys.api.discovery.v1.operations.repair.FixInterferenceResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixMissingFaces` | `(ansys.api.discovery.v1.operations.repair.FixMissingFacesRequest) -> ansys.api.discovery.v1.operations.repair.FixMissingFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixShortEdges` | `(ansys.api.discovery.v1.operations.repair.FixShortEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FixShortEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixSmallCurves` | `(ansys.api.discovery.v1.operations.repair.FixSmallCurvesRequest) -> ansys.api.discovery.v1.operations.repair.FixSmallCurvesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixSmallFaces` | `(ansys.api.discovery.v1.operations.repair.FixSmallFacesRequest) -> ansys.api.discovery.v1.operations.repair.FixSmallFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixSplitEdges` | `(ansys.api.discovery.v1.operations.repair.FixSplitEdgesRequest) -> ansys.api.discovery.v1.operations.repair.FixSplitEdgesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FixStitchFaces` | `(ansys.api.discovery.v1.operations.repair.FixStitchFacesRequest) -> ansys.api.discovery.v1.operations.repair.FixStitchFacesResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `InspectGeometry` | `(ansys.api.discovery.v1.operations.repair.InspectGeometryRequest) -> ansys.api.discovery.v1.operations.repair.InspectGeometryResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `RepairGeometry` | `(ansys.api.discovery.v1.operations.repair.RepairGeometryRequest) -> ansys.api.discovery.v1.operations.repair.RepairGeometryResponse [client_streaming=False, server_streaming=False]` |
| `Repair` | `FindBadFaces` | `(ansys.api.discovery.v1.operations.repair.FindBadFacesRequest) -> ansys.api.discovery.v1.operations.repair.FindBadFacesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.operations.sketch_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Sketch` | `CreateSketchLine` | `(ansys.api.discovery.v1.operations.sketch.CreateSketchLineRequest) -> ansys.api.discovery.v1.operations.sketch.CreateSketchLineResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.assignments.beamassignment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BeamAssignment` | `Create` | `(ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentCreationRequest) -> ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `BeamAssignment` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BeamAssignment` | `SetBeamProfile` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BeamAssignment` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.assignments.beamassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `BeamAssignment` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.assignments.beamassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `BeamAssignment` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.assignments.beamassignment.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.assignments.boltassignment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BoltAssignment` | `Create` | `(ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentCreationRequest) -> ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltAssignment` | `SetLocation` | `(ansys.api.discovery.v1.physics.assignments.boltassignment.SetBoltLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltAssignment` | `SetBolt` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltAssignment` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.assignments.boltassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `BoltAssignment` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.assignments.boltassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `BoltAssignment` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.assignments.boltassignment.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.assignments.fanassignment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FanAssignment` | `CreateInternal` | `(ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentCreationRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `CreateExternal` | `(ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentCreationRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetFan` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetExternalFanSpecification` | `(ansys.api.discovery.v1.physics.assignments.fanassignment.SetExternalFanSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetExternalFanGaugePressure` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetInternalFanInletFace` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetInternalFanIsShrouded` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetInternalFanHubRadius` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetInternalFanTipRadius` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetInternalFanTotalHeat` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `SetInternalFanSpecifyTotalHeat` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `GetInternalById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.GetInternalSingleResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `GetInternalByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.GetInternalSingleResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `GetAllInternal` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.GetAllInternalResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `GetExternalById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.GetExternalSingleResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `GetExternalByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.GetExternalSingleResponse [client_streaming=False, server_streaming=False]` |
| `FanAssignment` | `GetAllExternal` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.assignments.fanassignment.GetAllExternalResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.assignments.filletweldassignment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FilletWeldAssignment` | `Create` | `(ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentCreationRequest) -> ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `FilletWeldAssignment` | `SetWeld` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FilletWeldAssignment` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.assignments.filletweldassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `FilletWeldAssignment` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.assignments.filletweldassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `FilletWeldAssignment` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.assignments.filletweldassignment.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.assignments.materialassignment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `MaterialAssignment` | `Create` | `(ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentCreationRequest) -> ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentCreationResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `SetMaterial` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `SetTemperatureMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `SetTemperatureInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `SetCompressibleFlowEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.assignments.materialassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.assignments.materialassignment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `MaterialAssignment` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.assignments.materialassignment.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.acceleration_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Acceleration` | `Create` | `(ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationCreationRequest) -> ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationCreationResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetOrientation` | `(ansys.api.discovery.v1.physics.SetDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetDX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetDY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetDZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetTranslationalMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetIsFixedDX` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetIsFixedDY` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `SetIsFixedDZ` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.acceleration.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.acceleration.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Acceleration` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.acceleration.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.bearing_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Bearing` | `Create` | `(ansys.api.discovery.v1.physics.conditions.bearing.BearingCreationRequest) -> ansys.api.discovery.v1.physics.conditions.bearing.BearingCreationResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `SetRadialForce` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `SetThrustForce` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `SetAngle` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.bearing.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.bearing.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Bearing` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.bearing.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.boltpreload_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `BoltPreload` | `CreateClampForce` | `(ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadClampForceCreationRequest) -> ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `CreateGripLength` | `(ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadGripLengthCreationRequest) -> ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `CreateTorque` | `(ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadTorqueCreationRequest) -> ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetSide1Location` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetSide2Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.boltpreload.SetBoltPreloadSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetClampForce` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetGripLength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetTorque` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetTorqueCoefficient` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetSpecifyBoltDiameter` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `SetShankDiameter` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.boltpreload.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.boltpreload.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `BoltPreload` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.boltpreload.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.convection_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Convection` | `Create` | `(ansys.api.discovery.v1.physics.conditions.convection.ConvectionCreationRequest) -> ansys.api.discovery.v1.physics.conditions.convection.ConvectionCreationResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `SetCoefficientMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `SetTemperatureMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.convection.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.convection.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Convection` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.convection.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.current_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Current` | `Create` | `(ansys.api.discovery.v1.physics.conditions.current.CurrentCreationRequest) -> ansys.api.discovery.v1.physics.conditions.current.CurrentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.current.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.current.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Current` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.current.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.displacement_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Displacement` | `CreateTranslation` | `(ansys.api.discovery.v1.physics.conditions.displacement.DisplacementTranslationCreationRequest) -> ansys.api.discovery.v1.physics.conditions.displacement.DisplacementCreationResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `CreateRotation` | `(ansys.api.discovery.v1.physics.conditions.displacement.DisplacementRotationCreationRequest) -> ansys.api.discovery.v1.physics.conditions.displacement.DisplacementCreationResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `CreateCombined` | `(ansys.api.discovery.v1.physics.conditions.displacement.DisplacementCombinedCreationRequest) -> ansys.api.discovery.v1.physics.conditions.displacement.DisplacementCreationResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.displacement.ChangeDisplacementSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetOrientation` | `(ansys.api.discovery.v1.physics.SetDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetDX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetDY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetDZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetTranslationalMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetRX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetRY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetRZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetRotationalMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetIsFixedDX` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetIsFixedDY` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetIsFixedDZ` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetIsFixedRX` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetIsFixedRY` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetIsFixedRZ` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetUseRemotePointEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetDistributedRemotePositionX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetDistributedRemotePositionY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `SetDistributedRemotePositionZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.displacement.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.displacement.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Displacement` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.displacement.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.flow_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Flow` | `CreateVelocityInlet` | `(ansys.api.discovery.v1.physics.conditions.flow.FlowVelocityInletCreationRequest) -> ansys.api.discovery.v1.physics.conditions.flow.FlowVelocityInletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateVelocityOutlet` | `(ansys.api.discovery.v1.physics.conditions.flow.FlowVelocityOutletCreationRequest) -> ansys.api.discovery.v1.physics.conditions.flow.FlowVelocityOutletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreatePressureInlet` | `(ansys.api.discovery.v1.physics.conditions.flow.FlowPressureInletCreationRequest) -> ansys.api.discovery.v1.physics.conditions.flow.FlowPressureInletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreatePressureOutlet` | `(ansys.api.discovery.v1.physics.conditions.flow.FlowPressureOutletCreationRequest) -> ansys.api.discovery.v1.physics.conditions.flow.FlowPressureOutletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateMassFlowInlet` | `(ansys.api.discovery.v1.physics.conditions.flow.FlowMassFlowInletCreationRequest) -> ansys.api.discovery.v1.physics.conditions.flow.FlowMassFlowInletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `CreateMassFlowOutlet` | `(ansys.api.discovery.v1.physics.conditions.flow.FlowMassFlowOutletCreationRequest) -> ansys.api.discovery.v1.physics.conditions.flow.FlowMassFlowOutletCreationResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetVelocityInletMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetInletFlowComponentsVelocity` | `(ansys.api.discovery.v1.SetQuantityVectorRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetVelocityOutletMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetPressureInletMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetPressureOutletMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetMassFlowInletMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetMassFlowOutletMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetTemperatureInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetTemperatureMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetSwirlingInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetSwirlingMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.flow.SetFlowSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `SetDirection` | `(ansys.api.discovery.v1.physics.conditions.flow.SetFlowDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.flow.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.flow.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Flow` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.flow.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.fluidinitialtemperature_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FluidInitialTemperature` | `SetTemperatureMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInitialTemperature` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.fluidinitialtemperature.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `FluidInitialTemperature` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.fluidinitialtemperature.GetSingleResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.force_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Force` | `CreateDistributedTotal` | `(ansys.api.discovery.v1.physics.conditions.force.ForceDistributedTotalCreationRequest) -> ansys.api.discovery.v1.physics.conditions.force.ForceDistributedTotalCreationResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `CreateDistributedArea` | `(ansys.api.discovery.v1.physics.conditions.force.ForceDistributedAreaCreationRequest) -> ansys.api.discovery.v1.physics.conditions.force.ForceDistributedAreaCreationResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `CreateTorque` | `(ansys.api.discovery.v1.physics.conditions.force.ForceTorqueCreationRequest) -> ansys.api.discovery.v1.physics.conditions.force.ForceTorqueCreationResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.force.SetForceSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetMagnitudeDefinition` | `(ansys.api.discovery.v1.physics.conditions.force.SetForceMagnitudeDefinitionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `ReverseDirection` | `(ansys.api.discovery.v1.physics.CommandRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDefinedByComponentEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedTotalMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedTotalX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedTotalY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedTotalZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedAreaMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedAreaX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedAreaY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedAreaZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetUseRemoteForceEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedRemotePositionX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedRemotePositionY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetDistributedRemotePositionZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetTorqueMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetTorqueX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetTorqueY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `SetTorqueZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.force.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.force.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Force` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.force.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.gravity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Gravity` | `SetOrientation` | `(ansys.api.discovery.v1.physics.SetDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `SetDX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `SetDY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `SetDZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `SetTranslationalMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `SetUseBuoyancyEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `SetIncludeSelfWeightEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.gravity.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.gravity.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Gravity` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.gravity.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.heat_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Heat` | `CreateVolumetricTotal` | `(ansys.api.discovery.v1.physics.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v1.physics.conditions.heat.HeatTotalCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `CreateVolumetricDistributed` | `(ansys.api.discovery.v1.physics.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v1.physics.conditions.heat.HeatVolumetricDistributedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `CreateSurfaceTotal` | `(ansys.api.discovery.v1.physics.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v1.physics.conditions.heat.HeatTotalCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `CreateSurfaceDistributed` | `(ansys.api.discovery.v1.physics.conditions.heat.HeatCreationRequest) -> ansys.api.discovery.v1.physics.conditions.heat.HeatSurfaceDistributedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `SetTotalHeat` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `SetHeatPerUnitVolume` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `SetHeatPerUnitArea` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.heat.SetHeatSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.heat.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.heat.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Heat` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.heat.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.insulated_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Insulated` | `Create` | `(ansys.api.discovery.v1.physics.conditions.insulated.InsulatedCreationRequest) -> ansys.api.discovery.v1.physics.conditions.insulated.InsulatedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Insulated` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Insulated` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.insulated.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Insulated` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.insulated.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Insulated` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.insulated.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.localfidelity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `LocalFidelity` | `Create` | `(ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityCreationRequest) -> ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityCreationResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.localfidelity.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.localfidelity.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `LocalFidelity` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.localfidelity.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.mass_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Mass` | `Create` | `(ansys.api.discovery.v1.physics.conditions.mass.MassCreationRequest) -> ansys.api.discovery.v1.physics.conditions.mass.MassCreationResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `SetUseRemotePointEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `SetRemotePositionX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `SetRemotePositionY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `SetRemotePositionZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.mass.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.mass.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Mass` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.mass.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.moment_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Moment` | `CreateLocal` | `(ansys.api.discovery.v1.physics.conditions.moment.MomentCreationRequest) -> ansys.api.discovery.v1.physics.conditions.moment.MomentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `CreateGlobal` | `(ansys.api.discovery.v1.physics.conditions.moment.MomentCreationRequest) -> ansys.api.discovery.v1.physics.conditions.moment.MomentCreationResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.moment.SetMomentSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetOrientation` | `(ansys.api.discovery.v1.physics.SetDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetLocalX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetLocalY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetLocalZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetGlobalX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetGlobalY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `SetGlobalZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.moment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.moment.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Moment` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.moment.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.operatingpressure_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `OperatingPressure` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `OperatingPressure` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.operatingpressure.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `OperatingPressure` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.operatingpressure.GetSingleResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.porous_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Porous` | `CreateIsotropic` | `(ansys.api.discovery.v1.physics.conditions.porous.PorousCreationRequest) -> ansys.api.discovery.v1.physics.conditions.porous.PorousCreationResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `CreateBidirectional` | `(ansys.api.discovery.v1.physics.conditions.porous.PorousCreationRequest) -> ansys.api.discovery.v1.physics.conditions.porous.PorousCreationResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `CreateOrthotropic` | `(ansys.api.discovery.v1.physics.conditions.porous.PorousCreationRequest) -> ansys.api.discovery.v1.physics.conditions.porous.PorousCreationResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.porous.SetPorousSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetStreamwiseFlowDirectionReference` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetViscousStreamwiseMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetInertialStreamwiseMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetViscousCrossflowPrimaryMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetInertialCrossflowPrimaryMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetViscousCrossflowSecondaryMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetInertialCrossflowSecondaryMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetThermalInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetSolidPorosity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetSolidDensity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetSolidIsotropicThermalConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `SetSolidSpecificHeat` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.porous.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.porous.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Porous` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.porous.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.pressure_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Pressure` | `Create` | `(ansys.api.discovery.v1.physics.conditions.pressure.PressureCreationRequest) -> ansys.api.discovery.v1.physics.conditions.pressure.PressureCreationResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.pressure.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.pressure.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Pressure` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.pressure.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.rotatingfluidzone_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `RotatingFluidZone` | `Create` | `(ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneCreationRequest) -> ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneCreationResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `SetRotationalVelocityMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `RotatingFluidZone` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.solidtemperature_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SolidTemperature` | `CreateVolumetric` | `(ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureCreationRequest) -> ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureCreationResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `CreateSurface` | `(ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureCreationRequest) -> ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureCreationResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.solidtemperature.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.solidtemperature.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `SolidTemperature` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.solidtemperature.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.springpreload_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `SpringPreload` | `CreateLongitudinal` | `(ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadLongitudinalCreationRequest) -> ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `CreateTorsional` | `(ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadTorsionalCreationRequest) -> ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadCreationResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetSide1Location` | `(ansys.api.discovery.v1.SetLocationExtendedRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetSide2Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.springpreload.SetSpringPreloadSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetLongitudinalStiffness` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetTorsionalStiffness` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetType` | `(ansys.api.discovery.v1.physics.conditions.springpreload.SetSpringPreloadTypeRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetForce` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetTorque` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetLength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `SetRotation` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.springpreload.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.springpreload.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `SpringPreload` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.springpreload.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.support_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Support` | `CreateFixed` | `(ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateHinged` | `(ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateSliding` | `(ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateBall` | `(ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationRequest) -> ansys.api.discovery.v1.physics.conditions.support.SupportGeneralCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `CreateDisplaced` | `(ansys.api.discovery.v1.physics.conditions.support.SupportDisplacedCreationRequest) -> ansys.api.discovery.v1.physics.conditions.support.SupportDisplacedCreationResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.support.SetSupportSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedOrientation` | `(ansys.api.discovery.v1.physics.SetDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedDX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedDY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedDZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedRX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedRY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedRZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedIsFixedDX` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedIsFixedDY` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedIsFixedDZ` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedIsFixedRX` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedIsFixedRY` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `SetDisplacedIsFixedRZ` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.support.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.support.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Support` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.support.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.symmetry_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Symmetry` | `Create` | `(ansys.api.discovery.v1.physics.conditions.symmetry.SymmetryCreationRequest) -> ansys.api.discovery.v1.physics.conditions.symmetry.SymmetryCreationResponse [client_streaming=False, server_streaming=False]` |
| `Symmetry` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Symmetry` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.symmetry.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Symmetry` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.symmetry.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Symmetry` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.symmetry.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.velocity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Velocity` | `Create` | `(ansys.api.discovery.v1.physics.conditions.velocity.VelocityCreationRequest) -> ansys.api.discovery.v1.physics.conditions.velocity.VelocityCreationResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetOrientation` | `(ansys.api.discovery.v1.physics.SetDirectionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRotationalMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetIsFixedRX` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetIsFixedRY` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetIsFixedRZ` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetUseRemotePointEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRemotePositionX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRemotePositionY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `SetRemotePositionZ` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.velocity.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.velocity.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Velocity` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.velocity.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.voltage_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Voltage` | `Create` | `(ansys.api.discovery.v1.physics.conditions.voltage.VoltageCreationRequest) -> ansys.api.discovery.v1.physics.conditions.voltage.VoltageCreationResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `SetMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.voltage.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.voltage.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Voltage` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.voltage.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.conditions.wall_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Wall` | `CreateFreeSlip` | `(ansys.api.discovery.v1.physics.conditions.wall.WallFreeSlipCreationRequest) -> ansys.api.discovery.v1.physics.conditions.wall.WallFreeSlipCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `CreateStationary` | `(ansys.api.discovery.v1.physics.conditions.wall.WallStationaryCreationRequest) -> ansys.api.discovery.v1.physics.conditions.wall.WallStationaryCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `CreateTranslating` | `(ansys.api.discovery.v1.physics.conditions.wall.WallTranslationCreationRequest) -> ansys.api.discovery.v1.physics.conditions.wall.WallTranslationCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `CreateRotating` | `(ansys.api.discovery.v1.physics.conditions.wall.WallRotationCreationRequest) -> ansys.api.discovery.v1.physics.conditions.wall.WallRotationCreationResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetSpecification` | `(ansys.api.discovery.v1.physics.conditions.wall.SetWallSpecificationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetLocation` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetRotationalVelocityMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetTranslationalVelocityMagnitude` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetTranslationalVelocityX` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetTranslationalVelocityY` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetThermalInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetThermalOption` | `(ansys.api.discovery.v1.physics.conditions.wall.SetWallThermalOptionRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetInternalRadiationInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetExternalRadiationInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetInternalEmissivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetExternalTemperature` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetConvectionCoefficient` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetHeatFlux` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetHeatFlow` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetTemperature` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `SetExternalEmissivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.conditions.wall.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.conditions.wall.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Wall` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.conditions.wall.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.connections.contact_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Contact` | `Create` | `(ansys.api.discovery.v1.physics.connections.contact.ContactCreationRequest) -> ansys.api.discovery.v1.physics.connections.contact.ContactCreationResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetSide1Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetSide2Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetType` | `(ansys.api.discovery.v1.physics.SetContactTypeRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetPairs` | `(ansys.api.discovery.v1.physics.connections.contact.ChangeContactPairRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetFrictionCoefficient` | `(ansys.api.discovery.v1.SetUnitlessDoubleRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetStiffnessFactor` | `(ansys.api.discovery.v1.SetUnitlessDoubleRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetDetectionRadiusFactor` | `(ansys.api.discovery.v1.SetUnitlessDoubleRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetOffset` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetShearStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetTensileStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetAreStrengthLimitsSetEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetAdjustGapOrOverlapEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetMakeJustTouchingEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetIdealizeEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetThermalConductanceMethod` | `(ansys.api.discovery.v1.physics.SetConductanceMethodRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetElectricConductanceMethod` | `(ansys.api.discovery.v1.physics.SetConductanceMethodRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetConductanceMaterialThickness` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetConductanceMaterial` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetThermalContactConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetElectricContactConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetThermalContactConductance` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `SetElectricContactConductance` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `Split` | `(ansys.api.discovery.v1.physics.CommandRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.connections.contact.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.connections.contact.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Contact` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.connections.contact.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.connections.contactgroup_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `ContactGroup` | `SetSide1Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetSide2Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetType` | `(ansys.api.discovery.v1.physics.SetContactTypeRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `Split` | `(ansys.api.discovery.v1.physics.CommandRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `ConvertContactGroup` | `(ansys.api.discovery.v1.physics.connections.contactgroup.ConvertContactGroupChangeRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetFrictionCoefficient` | `(ansys.api.discovery.v1.SetUnitlessDoubleRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetStiffnessFactor` | `(ansys.api.discovery.v1.SetUnitlessDoubleRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetDetectionRadiusFactor` | `(ansys.api.discovery.v1.SetUnitlessDoubleRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetOffset` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetShearStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetTensileStrength` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetAreStrengthLimitsSetEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetAdjustGapOrOverlapEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetMakeJustTouchingEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetIdealizeEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetDetectionDistanceLow` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetDetectionDistanceHigh` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetThermalConductanceMethod` | `(ansys.api.discovery.v1.physics.SetConductanceMethodRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetElectricConductanceMethod` | `(ansys.api.discovery.v1.physics.SetConductanceMethodRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetConductanceMaterialThickness` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetConductanceMaterial` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetThermalContactConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetElectricContactConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetThermalContactConductance` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `SetElectricContactConductance` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.connections.contactgroup.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.connections.contactgroup.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `ContactGroup` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.connections.contactgroup.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.connections.fluidinterface_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `FluidInterface` | `SetType` | `(ansys.api.discovery.v1.physics.connections.fluidinterface.SetFluidInterfaceTypeRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFaceGroupingMethod` | `(ansys.api.discovery.v1.physics.connections.fluidinterface.SetFluidInterfaceFaceGroupingMethodRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetThermalConductanceMethod` | `(ansys.api.discovery.v1.physics.SetConductanceMethodRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetDetectionDistanceHigh` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFaceOverlapAllowance` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFSInterfaceThermalMaterialAssignment` | `(ansys.api.discovery.v1.SetAssignmentRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFSInterfaceThermalConductance` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFSInterfaceThermalConductivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFSInterfaceThermalThickness` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFSInterfaceInternalRadiationInputEnabled` | `(ansys.api.discovery.v1.SetBooleanRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `SetFSInterfaceInternalEmissivity` | `(ansys.api.discovery.v1.SetQuantityRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.connections.fluidinterface.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.connections.fluidinterface.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `FluidInterface` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.connections.fluidinterface.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.connections.joint_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Joint` | `Create` | `(ansys.api.discovery.v1.physics.connections.joint.JointCreationRequest) -> ansys.api.discovery.v1.physics.connections.joint.JointCreationResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `SetSide1Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `SetSide2Location` | `(ansys.api.discovery.v1.SetLocationRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `SetType` | `(ansys.api.discovery.v1.physics.connections.joint.SetJointTypeRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `GetById` | `(ansys.api.discovery.v1.GetByIdRequest) -> ansys.api.discovery.v1.physics.connections.joint.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `GetByLabel` | `(ansys.api.discovery.v1.GetByLabelRequest) -> ansys.api.discovery.v1.physics.connections.joint.GetSingleResponse [client_streaming=False, server_streaming=False]` |
| `Joint` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.connections.joint.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.parameterization.definedvariation_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `DefinedVariation` | `Create` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.CreateRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.CreateResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetAll` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetAllRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetAllResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetInput` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetInputRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetInputResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetOutput` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetOutputRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetOutputResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `Get` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `IsSolving` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.IsSolvingRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.IsSolvingResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `SetStarred` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetStarredRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetStarredResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetStarred` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetStarredRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetStarredResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `SetCurrent` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetCurrentRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetCurrentResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetCurrent` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetCurrentRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetCurrentResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetPreScript` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetScriptRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetScriptResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `GetPostScript` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetScriptRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetScriptResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `SetPreScript` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetScriptRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetScriptResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `SetPostScript` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetScriptRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetScriptResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `DeletePreScript` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.DeleteScriptRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.DeleteScriptResponse [client_streaming=False, server_streaming=False]` |
| `DefinedVariation` | `DeletePostScript` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.DeleteScriptRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.DeleteScriptResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.parameterization.parameter_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Parameter` | `GetAllInputs` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetAllInputsRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetAllInputsResponse [client_streaming=False, server_streaming=False]` |
| `Parameter` | `GetAllOutputs` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetAllOutputsRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.GetAllOutputsResponse [client_streaming=False, server_streaming=False]` |
| `Parameter` | `SetInputValue` | `(ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetInputValueRequest) -> ansys.api.discovery.v1.physics.parameterization.definedvariationstable.SetInputValueResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.physicsentity_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `PhysicsEntity` | `Delete` | `(ansys.api.discovery.v1.physics.physicsentity.DeleteRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `PhysicsEntity` | `SetSuppressionState` | `(ansys.api.discovery.v1.physics.physicsentity.SetSuppressionStateRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |
| `PhysicsEntity` | `SetName` | `(ansys.api.discovery.v1.physics.physicsentity.SetNameRequest) -> ansys.api.discovery.v1.SetResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.simulation.monitors_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Monitors` | `Create` | `(ansys.api.discovery.v1.physics.simulation.monitors.CreateMonitorRequest) -> ansys.api.discovery.v1.physics.simulation.monitors.MonitorCreationResponse [client_streaming=False, server_streaming=False]` |
| `Monitors` | `GetAll` | `(ansys.api.discovery.v1.physics.simulation.monitors.GetAllMonitorsRequest) -> ansys.api.discovery.v1.physics.simulation.monitors.GetAllMonitorsResponse [client_streaming=False, server_streaming=False]` |
| `Monitors` | `GetValues` | `(ansys.api.discovery.v1.physics.simulation.monitors.GetMonitorValuesRequest) -> ansys.api.discovery.v1.physics.simulation.monitors.GetMonitorValuesResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.simulation.simulations_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Simulations` | `Create` | `(ansys.api.discovery.v1.physics.simulation.simulations.CreateSimulationRequest) -> ansys.api.discovery.v1.physics.simulation.simulations.CreateSimulationResponse [client_streaming=False, server_streaming=False]` |
| `Simulations` | `GetAll` | `(ansys.api.discovery.v1.ParentEntityRequest) -> ansys.api.discovery.v1.physics.simulation.simulations.GetAllResponse [client_streaming=False, server_streaming=False]` |

### `ansys.api.discovery.v1.physics.simulation.solutions_pb2`

| Service | RPC method | Signature |
| --- | --- | --- |
| `Solutions` | `GetSolverFidelity` | `(ansys.api.discovery.v1.physics.simulation.solutions.GetSolverFidelityRequest) -> ansys.api.discovery.v1.physics.simulation.solutions.GetSolverFidelityResponse [client_streaming=False, server_streaming=False]` |
| `Solutions` | `SetSolverFidelity` | `(ansys.api.discovery.v1.physics.simulation.solutions.SetSolverFidelityRequest) -> ansys.api.discovery.v1.physics.simulation.solutions.SetSolverFidelityResponse [client_streaming=False, server_streaming=False]` |
| `Solutions` | `Solve` | `(ansys.api.discovery.v1.physics.simulation.solutions.SolveExecutionRequest) -> ansys.api.discovery.v1.physics.simulation.solutions.SolveExecutionResponse [client_streaming=False, server_streaming=False]` |

## Messages and fields

### `ansys.api.discovery.v0.assignments.boltassignment_pb2`

| Message | Fields |
| --- | --- |
| `BoltAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`bolt_assignment_properties: ansys.api.discovery.v0.assignments.boltassignment.BoltAssignmentProperties` (Protobuf field number 2; repeated=False) |
| `BoltAssignmentCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.assignments.boltassignment.BoltAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `BoltAssignmentDefinition` | `id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`bolt: ansys.api.discovery.v0.assignments.boltassignment.BoltAssignmentProperties` (Protobuf field number 6; repeated=False) |
| `BoltAssignmentProperties` | `definition: ansys.api.discovery.v0.engineeringdata.boltdata.BoltDataDefinition` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.assignments.fan_pb2`

| Message | Fields |
| --- | --- |
| `ChangeExternalFanSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v0.assignments.fanassignment.ExternalFanSpecification` (Protobuf field number 2; repeated=False) |
| `ExternalFanAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`fan_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`external_fan_assignment_properties: ansys.api.discovery.v0.assignments.fanassignment.ExternalFanAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `ExternalFanAssignmentCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.assignments.fanassignment.ExternalFanAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `ExternalFanAssignmentDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`assignment_properties: ansys.api.discovery.v0.assignments.fanassignment.InternalFanAssignmentProperties` (Protobuf field number 6; repeated=False)<br>`fan_properties: ansys.api.discovery.v0.engineeringdata.fandata.FanDataProperties` (Protobuf field number 7; repeated=False) |
| `ExternalFanAssignmentProperties` | `specification: ansys.api.discovery.v0.assignments.fanassignment.ExternalFanSpecification` (Protobuf field number 1; repeated=False)<br>`gauge_pressure: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`is_swirling: bool` (Protobuf field number 3; repeated=False) |
| `InternalFanAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`fan_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`internal_fan_assignment_properties: ansys.api.discovery.v0.assignments.fanassignment.InternalFanAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `InternalFanAssignmentCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.assignments.fanassignment.InternalFanAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `InternalFanAssignmentDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`assignment_properties: ansys.api.discovery.v0.assignments.fanassignment.ExternalFanAssignmentProperties` (Protobuf field number 6; repeated=False)<br>`fan_properties: ansys.api.discovery.v0.engineeringdata.fandata.FanDataProperties` (Protobuf field number 7; repeated=False) |
| `InternalFanAssignmentProperties` | `is_shrouded: bool` (Protobuf field number 1; repeated=False)<br>`specify_total_heat: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`hub_radius: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False)<br>`tip_radius: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False)<br>`is_swirling: bool` (Protobuf field number 5; repeated=False)<br>`inlet_face: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 6; repeated=False) |

### `ansys.api.discovery.v0.conditions.acceleration_pb2`

| Message | Fields |
| --- | --- |
| `AccelerationCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`acceleration_properties: ansys.api.discovery.v0.conditions.acceleration.AccelerationProperties` (Protobuf field number 2; repeated=False) |
| `AccelerationCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.acceleration.AccelerationDefinition` (Protobuf field number 2; repeated=False) |
| `AccelerationDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`acceleration: ansys.api.discovery.v0.conditions.acceleration.AccelerationProperties` (Protobuf field number 6; repeated=False) |
| `AccelerationProperties` | `acceleration: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.bearing_pb2`

| Message | Fields |
| --- | --- |
| `BearingCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`bearing_properties: ansys.api.discovery.v0.conditions.bearing.BearingProperties` (Protobuf field number 2; repeated=False) |
| `BearingCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.bearing.BearingDefinition` (Protobuf field number 2; repeated=False) |
| `BearingDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`bearing: ansys.api.discovery.v0.conditions.bearing.BearingProperties` (Protobuf field number 6; repeated=False) |
| `BearingProperties` | `radial_force: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`thrust_force: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`angle: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v0.conditions.boltpreload_pb2`

| Message | Fields |
| --- | --- |
| `BoltPreloadClampForceCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`clamp_force_properties: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadClampForceProperties` (Protobuf field number 2; repeated=False) |
| `BoltPreloadClampForceProperties` | `clamp_force: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |
| `BoltPreloadCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadDefinition` (Protobuf field number 2; repeated=False) |
| `BoltPreloadDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`side1_locations: string` (Protobuf field number 4; repeated=True)<br>`side2_locations: string` (Protobuf field number 5; repeated=True)<br>`suppressed: bool` (Protobuf field number 6; repeated=False)<br>`specification: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadSpecification` (Protobuf field number 7; repeated=False)<br>`clamp_force_properties: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadClampForceProperties` (Protobuf field number 8; repeated=False)<br>`grip_length_properties: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadGripLengthProperties` (Protobuf field number 9; repeated=False)<br>`torque_properties: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadTorqueProperties` (Protobuf field number 10; repeated=False) |
| `BoltPreloadGripLengthCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`grip_length_properties: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadGripLengthProperties` (Protobuf field number 2; repeated=False) |
| `BoltPreloadGripLengthProperties` | `grip_length: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |
| `BoltPreloadTorqueCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`torque_properties: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadTorqueProperties` (Protobuf field number 2; repeated=False) |
| `BoltPreloadTorqueProperties` | `torque: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`torque_coefficient: double` (Protobuf field number 2; repeated=False)<br>`boltdiameter: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 3; repeated=False) |
| `ChangeBoltPreloadSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v0.conditions.boltpreload.BoltPreloadSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.conditions.condition_pb2`

| Message | Fields |
| --- | --- |
| `ChangeConditionNameRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`new_name: string` (Protobuf field number 2; repeated=False) |
| `ChangeConditionSuppressionStateRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `DeleteConditionRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetByLabelRequest` | `label: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.convection_pb2`

| Message | Fields |
| --- | --- |
| `ConvectionCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`coefficient: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`temperature: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False) |
| `ConvectionCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.convection.ConvectionDefinition` (Protobuf field number 2; repeated=False) |
| `ConvectionDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`coefficient: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False)<br>`temperature: ansys.api.discovery.v0.Quantity` (Protobuf field number 7; repeated=False) |

### `ansys.api.discovery.v0.conditions.current_pb2`

| Message | Fields |
| --- | --- |
| `CurrentCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`current_properties: ansys.api.discovery.v0.conditions.current.CurrentProperties` (Protobuf field number 2; repeated=False) |
| `CurrentCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.current.CurrentDefinition` (Protobuf field number 2; repeated=False) |
| `CurrentDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`current: ansys.api.discovery.v0.conditions.current.CurrentProperties` (Protobuf field number 6; repeated=False) |
| `CurrentProperties` | `current_magnitude: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.displacement_pb2`

| Message | Fields |
| --- | --- |
| `ChangeDisplacementSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`displacement_specification: ansys.api.discovery.v0.conditions.displacement.DisplacementSpecification` (Protobuf field number 2; repeated=False) |
| `DisplacementCombinedCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`displacement_properties: ansys.api.discovery.v0.conditions.displacement.DisplacementCombinedProperties` (Protobuf field number 2; repeated=False) |
| `DisplacementCombinedProperties` | `displacement: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`rotation: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 2; repeated=False)<br>`remote_point: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 3; repeated=False) |
| `DisplacementCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.displacement.DisplacementDefinition` (Protobuf field number 2; repeated=False) |
| `DisplacementDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`displacement: ansys.api.discovery.v0.conditions.displacement.DisplacementCombinedProperties` (Protobuf field number 6; repeated=False) |
| `DisplacementRotationCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`displacement_properties: ansys.api.discovery.v0.conditions.displacement.DisplacementRotationProperties` (Protobuf field number 2; repeated=False) |
| `DisplacementRotationProperties` | `rotation: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 2; repeated=False) |
| `DisplacementTranslationCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`displacement_properties: ansys.api.discovery.v0.conditions.displacement.DisplacementTranslationProperties` (Protobuf field number 2; repeated=False) |
| `DisplacementTranslationProperties` | `displacement: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.conditions.flow_pb2`

| Message | Fields |
| --- | --- |
| `ChangeFlowDirectionRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.discovery.v0.conditions.flow.FlowDirectionDefinition` (Protobuf field number 2; repeated=False)<br>`reset_to_default_subtype: bool` (Protobuf field number 3; repeated=False) |
| `ChangeFlowSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v0.conditions.flow.FlowSpecificationDefinition` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowInletCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`mass_flow_inlet: ansys.api.discovery.v0.conditions.flow.MassFlowInletProperties` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowInletCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.flow.FlowMassFlowInletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowInletDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`mass_flow_inlet: ansys.api.discovery.v0.conditions.flow.MassFlowInletProperties` (Protobuf field number 6; repeated=False) |
| `FlowMassFlowOutletCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`mass_flow_outlet: ansys.api.discovery.v0.conditions.flow.MassFlowOutletProperties` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowOutletCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.flow.FlowMassFlowOutletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowOutletDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`mass_flow_outlet: ansys.api.discovery.v0.conditions.flow.MassFlowOutletProperties` (Protobuf field number 6; repeated=False) |
| `FlowPressureInletCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`pressure_inlet: ansys.api.discovery.v0.conditions.flow.PressureInletProperties` (Protobuf field number 2; repeated=False) |
| `FlowPressureInletCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.flow.FlowPressureInletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowPressureInletDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`pressure_inlet: ansys.api.discovery.v0.conditions.flow.PressureInletProperties` (Protobuf field number 6; repeated=False) |
| `FlowPressureOutletCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`pressure_outlet: ansys.api.discovery.v0.conditions.flow.PressureOutletProperties` (Protobuf field number 2; repeated=False) |
| `FlowPressureOutletCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.flow.FlowPressureOutletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowPressureOutletDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`pressure_outlet: ansys.api.discovery.v0.conditions.flow.PressureOutletProperties` (Protobuf field number 6; repeated=False) |
| `FlowThermalProperties` | `is_thermal: bool` (Protobuf field number 1; repeated=False)<br>`temperature: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False) |
| `FlowVelocityInletCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`velocity_inlet: ansys.api.discovery.v0.conditions.flow.VelocityInletProperties` (Protobuf field number 4; repeated=False) |
| `FlowVelocityInletCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.flow.FlowVelocityInletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowVelocityInletDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`velocity_inlet: ansys.api.discovery.v0.conditions.flow.VelocityInletProperties` (Protobuf field number 6; repeated=False) |
| `FlowVelocityOutletCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`velocity_outlet: ansys.api.discovery.v0.conditions.flow.VelocityOutletProperties` (Protobuf field number 2; repeated=False) |
| `FlowVelocityOutletCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.flow.FlowVelocityOutletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowVelocityOutletDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`velocity_outlet: ansys.api.discovery.v0.conditions.flow.VelocityOutletProperties` (Protobuf field number 6; repeated=False) |
| `MassFlowInletProperties` | `mass_flow: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v0.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False) |
| `MassFlowOutletProperties` | `mass_flow: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |
| `PressureInletProperties` | `pressure: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v0.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False) |
| `PressureOutletProperties` | `pressure: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v0.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False) |
| `VelocityInletProperties` | `speed: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v0.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False)<br>`is_swirling: bool` (Protobuf field number 3; repeated=False)<br>`rotational_speed: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False) |
| `VelocityOutletProperties` | `speed: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.force_pb2`

| Message | Fields |
| --- | --- |
| `ChangeForceMagnitudeDefinitionRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`force_magnitude_definition: ansys.api.discovery.v0.conditions.force.ForceMagnitudeDefinition` (Protobuf field number 2; repeated=False) |
| `ChangeForceSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`force_specification: ansys.api.discovery.v0.conditions.force.ForceSpecification` (Protobuf field number 2; repeated=False) |
| `ForceDistributedAreaCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`force_properties: ansys.api.discovery.v0.conditions.force.ForceDistributedProperties` (Protobuf field number 2; repeated=False) |
| `ForceDistributedAreaCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.force.ForceDistributedDefinition` (Protobuf field number 2; repeated=False) |
| `ForceDistributedDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`force_distributed: ansys.api.discovery.v0.conditions.force.ForceDistributedProperties` (Protobuf field number 6; repeated=False) |
| `ForceDistributedProperties` | `force: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`force_components: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 2; repeated=False)<br>`remote_point: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 3; repeated=False) |
| `ForceDistributedTotalCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`force_properties: ansys.api.discovery.v0.conditions.force.ForceDistributedProperties` (Protobuf field number 2; repeated=False) |
| `ForceDistributedTotalCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.force.ForceDistributedDefinition` (Protobuf field number 2; repeated=False) |
| `ForceTorqueCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`force_properties: ansys.api.discovery.v0.conditions.force.ForceTorqueProperties` (Protobuf field number 2; repeated=False) |
| `ForceTorqueCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.force.ForceTorqueDefinition` (Protobuf field number 2; repeated=False) |
| `ForceTorqueDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`force_torque: ansys.api.discovery.v0.conditions.force.ForceTorqueProperties` (Protobuf field number 6; repeated=False) |
| `ForceTorqueProperties` | `force: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`force_components: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.conditions.gravity_pb2`

| Message | Fields |
| --- | --- |
| `GravityDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`gravity: ansys.api.discovery.v0.conditions.gravity.GravityProperties` (Protobuf field number 6; repeated=False) |
| `GravityProperties` | `acceleration: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`include_buoyancy: bool` (Protobuf field number 2; repeated=False)<br>`include_self_weight: bool` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v0.conditions.heat_pb2`

| Message | Fields |
| --- | --- |
| `ChangeHeatSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`heat_specification: ansys.api.discovery.v0.conditions.heat.HeatSpecification` (Protobuf field number 2; repeated=False) |
| `HeatCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`heat: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False) |
| `HeatPerAreaDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`heat_per_unitarea: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False) |
| `HeatPerVolumeDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`heat_per_unitvolume: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False) |
| `HeatSurfaceDistributedCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.heat.HeatPerAreaDefinition` (Protobuf field number 2; repeated=False) |
| `HeatTotalCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.heat.HeatTotalDefinition` (Protobuf field number 2; repeated=False) |
| `HeatTotalDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`total_heat: ansys.api.discovery.v0.Quantity` (Protobuf field number 7; repeated=False) |
| `HeatVolumetricDistributedCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.heat.HeatPerVolumeDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.conditions.insulated_pb2`

| Message | Fields |
| --- | --- |
| `InsulatedCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False) |
| `InsulatedCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.insulated.InsulatedDefinition` (Protobuf field number 2; repeated=False) |
| `InsulatedDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False) |

### `ansys.api.discovery.v0.conditions.localfidelity_pb2`

| Message | Fields |
| --- | --- |
| `LocalFidelityCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`local_fidelity_properties: ansys.api.discovery.v0.conditions.localfidelity.LocalFidelityProperties` (Protobuf field number 2; repeated=False) |
| `LocalFidelityCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.localfidelity.LocalFidelityDefinition` (Protobuf field number 2; repeated=False) |
| `LocalFidelityDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`local_fidelity: ansys.api.discovery.v0.conditions.localfidelity.LocalFidelityProperties` (Protobuf field number 6; repeated=False) |
| `LocalFidelityProperties` | `local_fidelity_magnitude: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.mass_pb2`

| Message | Fields |
| --- | --- |
| `MassCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`mass_properties: ansys.api.discovery.v0.conditions.mass.MassProperties` (Protobuf field number 2; repeated=False) |
| `MassCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.mass.MassDefinition` (Protobuf field number 2; repeated=False) |
| `MassDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`mass: ansys.api.discovery.v0.conditions.mass.MassProperties` (Protobuf field number 6; repeated=False) |
| `MassProperties` | `mass_magnitude: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.conditions.moment_pb2`

| Message | Fields |
| --- | --- |
| `ChangeMomentSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`moment_specification: ansys.api.discovery.v0.conditions.moment.MomentSpecification` (Protobuf field number 2; repeated=False) |
| `MomentCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`moment_properties: ansys.api.discovery.v0.conditions.moment.MomentProperties` (Protobuf field number 2; repeated=False) |
| `MomentCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.moment.MomentDefinition` (Protobuf field number 2; repeated=False) |
| `MomentDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`local: ansys.api.discovery.v0.conditions.moment.MomentProperties` (Protobuf field number 6; repeated=False)<br>`global: ansys.api.discovery.v0.conditions.moment.MomentProperties` (Protobuf field number 7; repeated=False) |
| `MomentProperties` | `moment: ansys.api.discovery.v0.QuantityVector` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.porous_pb2`

| Message | Fields |
| --- | --- |
| `ChangePorousSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v0.conditions.porous.PorousSpecification` (Protobuf field number 2; repeated=False) |
| `PorousCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`porous_properties: ansys.api.discovery.v0.conditions.porous.PorousProperties` (Protobuf field number 2; repeated=False)<br>`streamwise_flow_direction_reference: ansys.api.discovery.v0.LocationIdentifier` (Protobuf field number 3; repeated=False) |
| `PorousCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.porous.PorousDefinition` (Protobuf field number 2; repeated=False) |
| `PorousDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`porous_properties: ansys.api.discovery.v0.conditions.porous.PorousProperties` (Protobuf field number 6; repeated=False)<br>`porous_specification: ansys.api.discovery.v0.conditions.porous.PorousSpecification` (Protobuf field number 7; repeated=False)<br>`streamwise_flow_direction_reference: ansys.api.discovery.v0.LocationIdentifier` (Protobuf field number 8; repeated=False) |
| `PorousProperties` | `coefficients: ansys.api.discovery.v0.conditions.porous.ResistanceCoeffients` (Protobuf field number 1; repeated=False)<br>`solid_properties: ansys.api.discovery.v0.conditions.porous.SolidProperties` (Protobuf field number 2; repeated=False) |
| `ResistanceCoeffients` | `viscous_streamwise: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`inertial_streamwise: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`viscous_primary: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False)<br>`inertial_primary: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False)<br>`viscous_secondary: ansys.api.discovery.v0.Quantity` (Protobuf field number 5; repeated=False)<br>`inertial_secondary: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False) |
| `SolidProperties` | `porosity: double` (Protobuf field number 1; repeated=False)<br>`density: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`isotropic_thermal_conductivity: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False)<br>`specific_heat: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False) |

### `ansys.api.discovery.v0.conditions.pressure_pb2`

| Message | Fields |
| --- | --- |
| `PressureCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`pressure_properties: ansys.api.discovery.v0.conditions.pressure.PressureProperties` (Protobuf field number 2; repeated=False) |
| `PressureCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.pressure.PressureDefinition` (Protobuf field number 2; repeated=False) |
| `PressureDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`pressure: ansys.api.discovery.v0.conditions.pressure.PressureProperties` (Protobuf field number 6; repeated=False) |
| `PressureProperties` | `pressure_magnitude: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.rotatingfluidzone_pb2`

| Message | Fields |
| --- | --- |
| `RotatingFluidZoneCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`rotating_fluid_zone_properties: ansys.api.discovery.v0.conditions.rotatingfluidzone.RotatingFluidZoneProperties` (Protobuf field number 4; repeated=False) |
| `RotatingFluidZoneCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.rotatingfluidzone.RotatingFluidZoneDefinition` (Protobuf field number 2; repeated=False) |
| `RotatingFluidZoneDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`rotating_fluid_zone_properties: ansys.api.discovery.v0.conditions.rotatingfluidzone.RotatingFluidZoneProperties` (Protobuf field number 6; repeated=False) |
| `RotatingFluidZoneProperties` | `rotational_velocity: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.solidtemperature_pb2`

| Message | Fields |
| --- | --- |
| `TemperatureCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`temperature: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False) |
| `TemperatureCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.solidtemperature.TemperatureDefinition` (Protobuf field number 2; repeated=False) |
| `TemperatureDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`magnitude: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False) |

### `ansys.api.discovery.v0.conditions.springpreload_pb2`

| Message | Fields |
| --- | --- |
| `ChangeSpringPreloadSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadSpecification` (Protobuf field number 2; repeated=False) |
| `ChangeSpringPreloadTypeRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`type: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadType` (Protobuf field number 2; repeated=False) |
| `SpringPreloadCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadDefinition` (Protobuf field number 2; repeated=False) |
| `SpringPreloadDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`side1_locations: string` (Protobuf field number 4; repeated=True)<br>`side2_locations: string` (Protobuf field number 5; repeated=True)<br>`suppressed: bool` (Protobuf field number 6; repeated=False)<br>`specification: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadSpecification` (Protobuf field number 7; repeated=False)<br>`longitudinal_stiffness_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadLongitudinalStiffnessProperties` (Protobuf field number 8; repeated=False)<br>`torsional_stiffness_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadTorsionalStiffnessProperties` (Protobuf field number 9; repeated=False)<br>`preload_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadProperties` (Protobuf field number 10; repeated=False) |
| `SpringPreloadLongitudinalCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`longitudinal_stiffness_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadLongitudinalStiffnessProperties` (Protobuf field number 3; repeated=False)<br>`preload_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadProperties` (Protobuf field number 4; repeated=False) |
| `SpringPreloadLongitudinalStiffnessProperties` | `longitudinal_stiffness: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |
| `SpringPreloadProperties` | `type: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadType` (Protobuf field number 1; repeated=False)<br>`preload_force: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`preload_length: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False)<br>`preload_torque: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False)<br>`preload_rotation: ansys.api.discovery.v0.Quantity` (Protobuf field number 5; repeated=False) |
| `SpringPreloadTorsionalCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`torsional_stiffness_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadTorsionalStiffnessProperties` (Protobuf field number 3; repeated=False)<br>`preload_properties: ansys.api.discovery.v0.conditions.springpreload.SpringPreloadProperties` (Protobuf field number 4; repeated=False) |
| `SpringPreloadTorsionalStiffnessProperties` | `torsional_stiffness: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.support_pb2`

| Message | Fields |
| --- | --- |
| `ChangeSupportSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`support_specification: ansys.api.discovery.v0.conditions.support.SupportSpecification` (Protobuf field number 2; repeated=False) |
| `GetAllRequest` | `parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `supports_general: ansys.api.discovery.v0.conditions.support.SupportGeneralDefinition` (Protobuf field number 1; repeated=True)<br>`supports_displaced: ansys.api.discovery.v0.conditions.support.SupportDisplacedDefinition` (Protobuf field number 2; repeated=True) |
| `SupportDisplacedCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`support_displaced: ansys.api.discovery.v0.conditions.support.SupportDisplacedProperties` (Protobuf field number 2; repeated=False) |
| `SupportDisplacedCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.support.SupportDisplacedDefinition` (Protobuf field number 2; repeated=False) |
| `SupportDisplacedDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`support_type: ansys.api.discovery.v0.conditions.support.SupportSpecification` (Protobuf field number 6; repeated=False)<br>`displacement: ansys.api.discovery.v0.TensorOfOptionalQuantities` (Protobuf field number 7; repeated=False) |
| `SupportDisplacedProperties` | `displacement: ansys.api.discovery.v0.TensorOfOptionalQuantities` (Protobuf field number 1; repeated=False) |
| `SupportGeneralCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False) |
| `SupportGeneralCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.support.SupportGeneralDefinition` (Protobuf field number 2; repeated=False) |
| `SupportGeneralDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`support_type: ansys.api.discovery.v0.conditions.support.SupportSpecification` (Protobuf field number 6; repeated=False) |

### `ansys.api.discovery.v0.conditions.symmetry_pb2`

| Message | Fields |
| --- | --- |
| `SymmetryCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False) |
| `SymmetryCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.symmetry.SymmetryDefinition` (Protobuf field number 2; repeated=False) |
| `SymmetryDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False) |

### `ansys.api.discovery.v0.conditions.velocity_pb2`

| Message | Fields |
| --- | --- |
| `VelocityCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`velocity_properties: ansys.api.discovery.v0.conditions.velocity.VelocityProperties` (Protobuf field number 2; repeated=False) |
| `VelocityCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.velocity.VelocityDefinition` (Protobuf field number 2; repeated=False) |
| `VelocityDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`velocity: ansys.api.discovery.v0.conditions.velocity.VelocityProperties` (Protobuf field number 6; repeated=False) |
| `VelocityProperties` | `velocity: ansys.api.discovery.v0.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v0.OptionalVector` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.conditions.voltage_pb2`

| Message | Fields |
| --- | --- |
| `VoltageCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`voltage_properties: ansys.api.discovery.v0.conditions.voltage.VoltageProperties` (Protobuf field number 2; repeated=False) |
| `VoltageCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.voltage.VoltageDefinition` (Protobuf field number 2; repeated=False) |
| `VoltageDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`voltage: ansys.api.discovery.v0.conditions.voltage.VoltageProperties` (Protobuf field number 6; repeated=False) |
| `VoltageProperties` | `voltage_magnitude: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.conditions.wall_pb2`

| Message | Fields |
| --- | --- |
| `ChangeWallSpecificationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`wall_specification: ansys.api.discovery.v0.conditions.wall.WallSpecification` (Protobuf field number 2; repeated=False) |
| `ChangeWallThermalOptionRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`wall_thermal_option: ansys.api.discovery.v0.conditions.wall.WallThermalOption` (Protobuf field number 2; repeated=False)<br>`is_external_radiation_enabled: bool` (Protobuf field number 3; repeated=False) |
| `FreeSlipProperties` | `wall_thermal_option_enabled: bool` (Protobuf field number 1; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v0.conditions.wall.WallThermalProperties` (Protobuf field number 2; repeated=False) |
| `RotationProperties` | `rotational_velocity: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`wall_thermal_option_enabled: bool` (Protobuf field number 2; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v0.conditions.wall.WallThermalProperties` (Protobuf field number 3; repeated=False) |
| `StationaryProperties` | `wall_thermal_option_enabled: bool` (Protobuf field number 1; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v0.conditions.wall.WallThermalProperties` (Protobuf field number 2; repeated=False) |
| `TranslationProperties` | `wall_thermal_option_enabled: bool` (Protobuf field number 1; repeated=False)<br>`translational_velocity: ansys.api.discovery.v0.QuantityVector` (Protobuf field number 2; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v0.conditions.wall.WallThermalProperties` (Protobuf field number 3; repeated=False) |
| `WallFreeSlipCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`freeslip_properties: ansys.api.discovery.v0.conditions.wall.FreeSlipProperties` (Protobuf field number 4; repeated=False) |
| `WallFreeSlipCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.wall.WallFreeSlipDefinition` (Protobuf field number 2; repeated=False) |
| `WallFreeSlipDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`free_slip_properties: ansys.api.discovery.v0.conditions.wall.FreeSlipProperties` (Protobuf field number 6; repeated=False) |
| `WallRotationCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`rotating_properties: ansys.api.discovery.v0.conditions.wall.RotationProperties` (Protobuf field number 4; repeated=False) |
| `WallRotationCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.wall.WallRotationDefinition` (Protobuf field number 2; repeated=False) |
| `WallRotationDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`rotation_properties: ansys.api.discovery.v0.conditions.wall.RotationProperties` (Protobuf field number 6; repeated=False) |
| `WallStationaryCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`stationary_properties: ansys.api.discovery.v0.conditions.wall.StationaryProperties` (Protobuf field number 4; repeated=False) |
| `WallStationaryCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.wall.WallStationaryDefinition` (Protobuf field number 2; repeated=False) |
| `WallStationaryDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`stationary_properties: ansys.api.discovery.v0.conditions.wall.StationaryProperties` (Protobuf field number 6; repeated=False) |
| `WallThermalProperties` | `wall_thermal_option: ansys.api.discovery.v0.conditions.wall.WallThermalOption` (Protobuf field number 1; repeated=False)<br>`internal_emissivity: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`external_temperature: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False)<br>`convection_coefficient: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False)<br>`heatflux: ansys.api.discovery.v0.Quantity` (Protobuf field number 5; repeated=False)<br>`heatflow: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False)<br>`temperature: ansys.api.discovery.v0.Quantity` (Protobuf field number 7; repeated=False)<br>`external_emissivity: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 8; repeated=False) |
| `WallTranslationCreationRequest` | `creation_data: ansys.api.discovery.v0.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`translating_properties: ansys.api.discovery.v0.conditions.wall.TranslationProperties` (Protobuf field number 4; repeated=False) |
| `WallTranslationCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.conditions.wall.WallTranslationDefinition` (Protobuf field number 2; repeated=False) |
| `WallTranslationDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`locations: string` (Protobuf field number 4; repeated=True)<br>`suppressed: bool` (Protobuf field number 5; repeated=False)<br>`translation_properties: ansys.api.discovery.v0.conditions.wall.TranslationProperties` (Protobuf field number 6; repeated=False) |

### `ansys.api.discovery.v0.connections.contact_pb2`

| Message | Fields |
| --- | --- |
| `ChangeContactPairRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`contact_pairs: ansys.api.discovery.v0.ContactPairs` (Protobuf field number 2; repeated=False) |
| `ChangeContactTypeRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`contact_type: ansys.api.discovery.v0.ContactType` (Protobuf field number 2; repeated=False) |
| `ContactCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`contact_properties: ansys.api.discovery.v0.ContactProperties` (Protobuf field number 2; repeated=False) |
| `ContactCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.connections.contact.ContactDefinition` (Protobuf field number 2; repeated=False) |
| `ContactDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`side1_locations: string` (Protobuf field number 4; repeated=True)<br>`side2_locations: string` (Protobuf field number 5; repeated=True)<br>`suppressed: bool` (Protobuf field number 6; repeated=False)<br>`contact: ansys.api.discovery.v0.ContactProperties` (Protobuf field number 7; repeated=False) |

### `ansys.api.discovery.v0.connections.contactgroup_pb2`

| Message | Fields |
| --- | --- |
| `ContactGroupDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`side1_locations: string` (Protobuf field number 4; repeated=True)<br>`side2_locations: string` (Protobuf field number 5; repeated=True)<br>`suppressed: bool` (Protobuf field number 6; repeated=False)<br>`contact: ansys.api.discovery.v0.ContactProperties` (Protobuf field number 7; repeated=False) |
| `ConvertContactGroupChangeRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`contact_group_type: ansys.api.discovery.v0.connections.contactgroup.ContactGoupConversionType` (Protobuf field number 2; repeated=False)<br>`contact_pairs: ansys.api.discovery.v0.ContactPairs` (Protobuf field number 3; repeated=False)<br>`idealize: bool` (Protobuf field number 4; repeated=False)<br>`friction_coefficient: double` (Protobuf field number 5; repeated=False) |

### `ansys.api.discovery.v0.connections.fluidinterface_pb2`

| Message | Fields |
| --- | --- |
| `ChangeFluidInterfaceFaceGroupingMethodRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`face_grouping_method: ansys.api.discovery.v0.connections.fluidinterface.FluidInterfaceFaceGroupingMethod` (Protobuf field number 2; repeated=False) |
| `ChangeFluidInterfaceTypeRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`interface_type: ansys.api.discovery.v0.connections.fluidinterface.FluidInterfaceType` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.connections.joint_pb2`

| Message | Fields |
| --- | --- |
| `ChangeJointTypeRequest` | `object_id: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`joint_type: ansys.api.discovery.v0.connections.joint.JointType` (Protobuf field number 2; repeated=False) |
| `JointCreationRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`joint_properties: ansys.api.discovery.v0.connections.joint.JointProperties` (Protobuf field number 2; repeated=False) |
| `JointCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.connections.joint.JointDefinition` (Protobuf field number 2; repeated=False) |
| `JointDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`side1_locations: string` (Protobuf field number 4; repeated=True)<br>`side2_locations: string` (Protobuf field number 5; repeated=True)<br>`suppressed: bool` (Protobuf field number 6; repeated=False)<br>`joint: ansys.api.discovery.v0.connections.joint.JointProperties` (Protobuf field number 7; repeated=False) |
| `JointProperties` | `joint_type: ansys.api.discovery.v0.connections.joint.JointType` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.definedvariationstable_pb2`

| Message | Fields |
| --- | --- |
| `GetAllInputsResponse` | `inputs: ansys.api.discovery.v0.InputColumn` (Protobuf field number 1; repeated=True) |
| `GetAllOutputsResponse` | `outputs: ansys.api.discovery.v0.OutputColumn` (Protobuf field number 1; repeated=True) |
| `GetAllVariationsResponse` | `defined_variations: ansys.api.discovery.v0.Variation` (Protobuf field number 1; repeated=True) |
| `GetCurrentVariationResponse` | `variation_moniker: string` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `GetInputColumnRequest` | `input_parameter_moniker: string` (Protobuf field number 1; repeated=False) |
| `GetInputColumnResponse` | `column: ansys.api.discovery.v0.InputColumn` (Protobuf field number 1; repeated=False) |
| `GetInputForVariationRequest` | `variation_moniker: string` (Protobuf field number 1; repeated=False)<br>`input_parameter_moniker: string` (Protobuf field number 2; repeated=False) |
| `GetOutputColumnRequest` | `output_parameter_moniker: string` (Protobuf field number 1; repeated=False) |
| `GetOutputColumnResponse` | `column: ansys.api.discovery.v0.OutputColumn` (Protobuf field number 1; repeated=False) |
| `GetOutputForVariationRequest` | `variation_moniker: string` (Protobuf field number 1; repeated=False)<br>`output_parameter_moniker: string` (Protobuf field number 2; repeated=False) |
| `IsSolvingResponse` | `is_solving: bool` (Protobuf field number 1; repeated=False) |
| `SetInputValueRequest` | `variation_moniker: string` (Protobuf field number 1; repeated=False)<br>`defined_variation_table_input: ansys.api.discovery.v0.InputParameter` (Protobuf field number 2; repeated=False) |
| `SetStarredStatusRequest` | `variations_monikers: string` (Protobuf field number 1; repeated=True)<br>`starred: bool` (Protobuf field number 2; repeated=False) |
| `UpdateResponse` | `result: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v0.discoverymodels_pb2`

| Message | Fields |
| --- | --- |
| `ChangeAssignmentRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`referenced_object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `ChangeBooleanRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`boolean_value: bool` (Protobuf field number 2; repeated=False) |
| `ChangeCommandRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `ChangeDirectionRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.geometry.v0.Direction` (Protobuf field number 2; repeated=False) |
| `ChangeDoubleRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `ChangeEmptyRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `ChangeLocationExtendedRequest` | `change_location_request: ansys.api.discovery.v0.ChangeLocationRequest` (Protobuf field number 1; repeated=False)<br>`location_type: ansys.api.dbu.v0.LocationType` (Protobuf field number 2; repeated=False) |
| `ChangeLocationRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`location_ids: string` (Protobuf field number 2; repeated=True) |
| `ChangeQuantityRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`quantity: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False) |
| `ChangeResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `ChangeSpecifyConductanceRequest` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`conductance_type: ansys.api.discovery.v0.ConductanceOptionType` (Protobuf field number 2; repeated=False) |
| `ContactPair` | `item1: string` (Protobuf field number 1; repeated=True)<br>`item2: string` (Protobuf field number 2; repeated=True) |
| `ContactPairs` | `contact_pair: ansys.api.discovery.v0.ContactPair` (Protobuf field number 1; repeated=True) |
| `ContactProperties` | `contact_type: ansys.api.discovery.v0.ContactType` (Protobuf field number 1; repeated=False)<br>`contact_pairs: ansys.api.discovery.v0.ContactPairs` (Protobuf field number 2; repeated=False)<br>`friction_coefficient: double` (Protobuf field number 3; repeated=False)<br>`stiffness_factor: double` (Protobuf field number 4; repeated=False)<br>`detection_radius_factor: double` (Protobuf field number 5; repeated=False)<br>`offset: ansys.api.discovery.v0.Quantity` (Protobuf field number 6; repeated=False)<br>`shear_strenght: ansys.api.discovery.v0.Quantity` (Protobuf field number 7; repeated=False)<br>`tensile_strength: ansys.api.discovery.v0.Quantity` (Protobuf field number 8; repeated=False)<br>`are_strength_limits_set: bool` (Protobuf field number 9; repeated=False)<br>`adjust_gap_or_overlap: bool` (Protobuf field number 10; repeated=False)<br>`make_just_touching: bool` (Protobuf field number 11; repeated=False)<br>`idealize: bool` (Protobuf field number 12; repeated=False)<br>`specify_thermal_conductance: bool` (Protobuf field number 13; repeated=False)<br>`specify_electric_conductance: bool` (Protobuf field number 14; repeated=False)<br>`thermal_contact_conductance: ansys.api.discovery.v0.Quantity` (Protobuf field number 15; repeated=False)<br>`thermal_contact_conductivity: ansys.api.discovery.v0.Quantity` (Protobuf field number 16; repeated=False)<br>`thermal_conductance_thickness: ansys.api.discovery.v0.Quantity` (Protobuf field number 17; repeated=False)<br>`electrical_contact_conductance: ansys.api.discovery.v0.Quantity` (Protobuf field number 18; repeated=False)<br>`electrical_contact_conductivity: ansys.api.discovery.v0.Quantity` (Protobuf field number 19; repeated=False)<br>`electrical_conductance_thickness: ansys.api.discovery.v0.Quantity` (Protobuf field number 20; repeated=False)<br>`thermal_conductance_option: ansys.api.discovery.v0.ConductanceOptionType` (Protobuf field number 21; repeated=False)<br>`electric_conductance_option: ansys.api.discovery.v0.ConductanceOptionType` (Protobuf field number 22; repeated=False) |
| `CreationResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `DoubleSidedScopedCreationData` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`side1_locations: ansys.api.discovery.v0.LocationIdentifier` (Protobuf field number 3; repeated=False)<br>`side2_locations: ansys.api.discovery.v0.LocationIdentifier` (Protobuf field number 4; repeated=False) |
| `HistoryTrackParameter` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`dimension_type: ansys.api.dbu.v0.DimensionType` (Protobuf field number 3; repeated=False)<br>`dimension_value: double` (Protobuf field number 4; repeated=False) |
| `InputColumn` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`range: string` (Protobuf field number 3; repeated=False)<br>`parameter_variations: ansys.api.discovery.v0.InputParameter` (Protobuf field number 4; repeated=True) |
| `InputParameter` | `id: string` (Protobuf field number 1; repeated=False)<br>`parent_id: string` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`quantity_type: ansys.api.discovery.v0.QuantityType` (Protobuf field number 4; repeated=False)<br>`quantity_value: double` (Protobuf field number 5; repeated=False)<br>`unit: int32` (Protobuf field number 6; repeated=False)<br>`unit_abbreviation: string` (Protobuf field number 7; repeated=False)<br>`input_type: ansys.api.discovery.v0.InputParameterType` (Protobuf field number 8; repeated=False)<br>`parent_object_id: string` (Protobuf field number 9; repeated=False)<br>`material_id: string` (Protobuf field number 10; repeated=False)<br>`material_label: string` (Protobuf field number 11; repeated=False) |
| `LocationIdentifier` | `location_ids: string` (Protobuf field number 1; repeated=True)<br>`location_type: ansys.api.dbu.v0.LocationType` (Protobuf field number 2; repeated=False) |
| `MessageResponse` | `message: string` (Protobuf field number 1; repeated=False) |
| `OptionalQuantity` | `is_defined: bool` (Protobuf field number 1; repeated=False)<br>`quantity: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False) |
| `OptionalVector` | `is_defined: bool` (Protobuf field number 1; repeated=False)<br>`vector: ansys.api.discovery.v0.QuantityVector` (Protobuf field number 2; repeated=False) |
| `OutputColumn` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`range: string` (Protobuf field number 3; repeated=False)<br>`parameter_variations: ansys.api.discovery.v0.OutputParameter` (Protobuf field number 4; repeated=True) |
| `OutputParameter` | `id: string` (Protobuf field number 1; repeated=False)<br>`parent_id: string` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`quantity_type: ansys.api.discovery.v0.QuantityType` (Protobuf field number 4; repeated=False)<br>`quantity_value: double` (Protobuf field number 5; repeated=False)<br>`unit: int32` (Protobuf field number 6; repeated=False)<br>`unit_abbreviation: string` (Protobuf field number 7; repeated=False) |
| `Quantity` | `quantity_type: ansys.api.discovery.v0.QuantityType` (Protobuf field number 1; repeated=False)<br>`quantity_value: double` (Protobuf field number 2; repeated=False)<br>`unit: int32` (Protobuf field number 3; repeated=False)<br>`unit_abbreviation: string` (Protobuf field number 4; repeated=False)<br>`as_string: string` (Protobuf field number 5; repeated=False) |
| `QuantityPair` | `independant_data: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`dependant_data: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False) |
| `QuantityPairTable` | `header: ansys.api.discovery.v0.TableHeader` (Protobuf field number 1; repeated=False)<br>`row_data: ansys.api.discovery.v0.QuantityPair` (Protobuf field number 2; repeated=True) |
| `QuantityTable` | `header: ansys.api.discovery.v0.TableHeader` (Protobuf field number 1; repeated=False)<br>`row_data: ansys.api.discovery.v0.QuantityTableRow` (Protobuf field number 2; repeated=True) |
| `QuantityTableRow` | `row_cells: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=True) |
| `QuantityVector` | `x: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=False)<br>`y: ansys.api.discovery.v0.Quantity` (Protobuf field number 2; repeated=False)<br>`z: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False) |
| `QuantityVectorTable` | `header: ansys.api.discovery.v0.TableHeader` (Protobuf field number 1; repeated=False)<br>`row_data: ansys.api.discovery.v0.QuantityVector` (Protobuf field number 2; repeated=True) |
| `ScopedCreationData` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`locations: ansys.api.discovery.v0.LocationIdentifier` (Protobuf field number 3; repeated=False) |
| `ScriptParameter` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`dimension_type: ansys.api.dbu.v0.DimensionType` (Protobuf field number 3; repeated=False)<br>`dimension_value: double` (Protobuf field number 4; repeated=False) |
| `Simulation` | `object_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`label: string` (Protobuf field number 2; repeated=False) |
| `TableHeader` | `table_name: string` (Protobuf field number 1; repeated=False)<br>`number_of_data_rows: int32` (Protobuf field number 2; repeated=False)<br>`number_of_data_columns: int32` (Protobuf field number 3; repeated=False) |
| `TensorOfOptionalQuantities` | `dx: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 1; repeated=False)<br>`dy: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`dz: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 3; repeated=False)<br>`rx: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 4; repeated=False)<br>`ry: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 5; repeated=False)<br>`rz: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 6; repeated=False) |
| `Variation` | `id: string` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`starred: bool` (Protobuf field number 3; repeated=False)<br>`inputs: ansys.api.discovery.v0.InputParameter` (Protobuf field number 4; repeated=True)<br>`outputs: ansys.api.discovery.v0.OutputParameter` (Protobuf field number 5; repeated=True) |
| `VectorOfOptionalQuantities` | `x: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 1; repeated=False)<br>`y: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`z: ansys.api.discovery.v0.OptionalQuantity` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v0.engineeringdata.boltdata_pb2`

| Message | Fields |
| --- | --- |
| `BoltDataCreationResponse` | `condition_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v0.engineeringdata.boltdata.BoltDataDefinition` (Protobuf field number 2; repeated=False) |
| `BoltDataDefinition` | `id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`suppressed: bool` (Protobuf field number 4; repeated=False)<br>`bolt: ansys.api.discovery.v0.engineeringdata.boltdata.BoltDataProperties` (Protobuf field number 5; repeated=False) |
| `BoltDataLibraryRequest` | `label: string` (Protobuf field number 1; repeated=False) |
| `BoltDataProperties` | `material_name: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.engineeringdata.fandata_pb2`

| Message | Fields |
| --- | --- |
| `FanCreationRequest` | `fan_data: ansys.api.discovery.v0.engineeringdata.fandata.FanDataProperties` (Protobuf field number 2; repeated=False) |
| `FanCreationResponse` | `data_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`engineering_data: ansys.api.discovery.v0.engineeringdata.fandata.FanDataDefinition` (Protobuf field number 2; repeated=False) |
| `FanDataDefinition` | `fan_data: ansys.api.discovery.v0.engineeringdata.fandata.FanDataProperties` (Protobuf field number 1; repeated=False) |
| `FanDataProperties` | `data_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`fan_name: string` (Protobuf field number 2; repeated=False)<br>`fan_specification: ansys.api.discovery.v0.engineeringdata.fandata.FanSpecification` (Protobuf field number 3; repeated=False)<br>`constant_pressure_rise: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False)<br>`volume_flow_rate_vs_pressure_table: ansys.api.discovery.v0.QuantityPairTable` (Protobuf field number 5; repeated=False)<br>`velocity_vs_pressure_table: ansys.api.discovery.v0.QuantityPairTable` (Protobuf field number 6; repeated=False)<br>`manufacturer_data: ansys.api.discovery.v0.engineeringdata.fandata.FanManufacturerData` (Protobuf field number 7; repeated=False) |
| `FanManufacturerData` | `manufacturer: string` (Protobuf field number 1; repeated=False)<br>`model_number: string` (Protobuf field number 2; repeated=False)<br>`outer_radius: ansys.api.discovery.v0.Quantity` (Protobuf field number 3; repeated=False)<br>`inner_radius: ansys.api.discovery.v0.Quantity` (Protobuf field number 4; repeated=False)<br>`notes: string` (Protobuf field number 5; repeated=False)<br>`disclaimer: string` (Protobuf field number 6; repeated=False)<br>`is_user_defined: bool` (Protobuf field number 7; repeated=False) |

### `ansys.api.discovery.v0.historytrackparameters_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `history_track_parameters: ansys.api.discovery.v0.HistoryTrackParameter` (Protobuf field number 1; repeated=True) |
| `GetRecordingStatusResponse` | `status: ansys.api.discovery.v0.historytrackparameters.RecordingStatus` (Protobuf field number 1; repeated=False) |
| `ReplayResponse` | `result: string` (Protobuf field number 1; repeated=False) |
| `SetRecordingStatusRequest` | `status: ansys.api.discovery.v0.historytrackparameters.RecordingStatus` (Protobuf field number 1; repeated=False) |
| `UpdateRequest` | `history_track_parameter: ansys.api.discovery.v0.HistoryTrackParameter` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.messaging_pb2`

| Message | Fields |
| --- | --- |
| `MessagingResponse` | `event_message: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.monitors_pb2`

| Message | Fields |
| --- | --- |
| `CreateMonitorRequest` | `creation_data: ansys.api.discovery.v0.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`monitor: ansys.api.discovery.v0.monitors.MonitorProperties` (Protobuf field number 2; repeated=False) |
| `GetAllMonitorsRequest` | — |
| `GetAllMonitorsResponse` | `monitor_definitions: ansys.api.discovery.v0.monitors.MonitorDefinition` (Protobuf field number 1; repeated=True) |
| `GetMonitorValuesRequest` | `monitor_id: string` (Protobuf field number 1; repeated=False) |
| `GetMonitorValuesResponse` | `monitor_values: ansys.api.discovery.v0.Quantity` (Protobuf field number 1; repeated=True) |
| `MonitorCreationResponse` | `monitor_response: ansys.api.discovery.v0.CreationResponse` (Protobuf field number 1; repeated=False)<br>`monitor: ansys.api.discovery.v0.monitors.MonitorDefinition` (Protobuf field number 2; repeated=False) |
| `MonitorDefinition` | `id: string` (Protobuf field number 1; repeated=False)<br>`label: string` (Protobuf field number 2; repeated=False)<br>`side1_locations: string` (Protobuf field number 3; repeated=True)<br>`side2_locations: string` (Protobuf field number 4; repeated=True)<br>`monitor: ansys.api.discovery.v0.monitors.MonitorProperties` (Protobuf field number 5; repeated=False) |
| `MonitorProperties` | `result_variable: ansys.api.discovery.v0.results.ResultVariable` (Protobuf field number 1; repeated=False)<br>`result_function: ansys.api.discovery.v0.results.ResultFunction` (Protobuf field number 2; repeated=False)<br>`result_component: ansys.api.discovery.v0.results.ResultComponent` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v0.scriptparameters_pb2`

| Message | Fields |
| --- | --- |
| `GetAllRequest` | `parent: string` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `script_parameters: ansys.api.discovery.v0.ScriptParameter` (Protobuf field number 1; repeated=True) |
| `ReplayResponse` | `result: string` (Protobuf field number 1; repeated=False) |
| `UpdateRequest` | `script_parameter: ansys.api.discovery.v0.ScriptParameter` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.simulations_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `simulations: ansys.api.discovery.v0.Simulation` (Protobuf field number 1; repeated=True) |

### `ansys.api.discovery.v0.solution_pb2`

| Message | Fields |
| --- | --- |
| `SimulationStageRequest` | `simulation_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`stage: string` (Protobuf field number 2; repeated=False) |
| `SolveExecutionRequest` | `simulation_id: ansys.api.dbu.v0.PhysicsEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`solver_manager: ansys.api.discovery.v0.solution.SolverManager` (Protobuf field number 2; repeated=False)<br>`execute_remotely: bool` (Protobuf field number 3; repeated=False)<br>`variation_id_list: string` (Protobuf field number 4; repeated=True) |
| `SolveExecutionResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `SolverFidelityRequest` | `simulation_stage: ansys.api.discovery.v0.solution.SimulationStageRequest` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `SolverFidelityResponse` | `value: double` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v0.unsupported_pb2`

| Message | Fields |
| --- | --- |
| `ByteArrayResponse` | `bytes: bytes` (Protobuf field number 1; repeated=False)<br>`success: bool` (Protobuf field number 2; repeated=False) |
| `CreateFacetedBodiesRequest` | `tessellation_data: ansys.api.discovery.v0.unsupported.CreateFacetedBodiesRequest.TessellationDataEntry` (Protobuf field number 1; repeated=True) |
| `CreateFacetedBodiesResponse` | `created_bodies: ansys.api.dbu.v0.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DoubleValueResponse` | `value: double` (Protobuf field number 1; repeated=False)<br>`success: bool` (Protobuf field number 2; repeated=False) |
| `VariableExportRequest` | `result_variables: ansys.api.discovery.v0.results.ResultVariable` (Protobuf field number 1; repeated=True) |
| `VariableExportRequestToFile` | `result_variables: ansys.api.discovery.v0.results.ResultVariable` (Protobuf field number 1; repeated=True)<br>`file_path: string` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.commands.application_pb2`

| Message | Fields |
| --- | --- |
| `ApplicationStartedRequest` | — |
| `ApplicationStartedResponse` | `is_startup_complete: bool` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `CloseApplicationRequest` | — |
| `CloseApplicationResponse` | `set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 1; repeated=False) |
| `DisposeTrackerRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `DisposeTrackerResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `GetBackendRequest` | — |
| `GetBackendResponse` | `type: ansys.api.discovery.v1.BackendType` (Protobuf field number 1; repeated=False)<br>`version: ansys.api.discovery.v1.commands.application.VersionIdentifier` (Protobuf field number 2; repeated=False)<br>`backend_version_info: string` (Protobuf field number 3; repeated=False)<br>`additional_build_info: ansys.api.discovery.v1.commands.application.GetBackendResponse.AdditionalBuildInfoEntry` (Protobuf field number 4; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 5; repeated=False) |
| `GetMonikerCompressionMethodRequest` | — |
| `GetMonikerCompressionMethodResponse` | `method: ansys.api.discovery.v1.MonikerCompressionMethod` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetTrackerChangesRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetTrackerChangesResponse` | `tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 1; repeated=False) |
| `GetTrackerRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetTrackerResponse` | `tracker: ansys.api.discovery.v1.commands.application.TrackerDefinition` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `RedoRequest` | `steps: int32` (Protobuf field number 1; repeated=False) |
| `RedoResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `SetApplicationTitleRequest` | `title: string` (Protobuf field number 1; repeated=False) |
| `SetApplicationTitleResponse` | `set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 1; repeated=False) |
| `SetAutomaticTrackingStateRequest` | `state: ansys.api.discovery.v1.AutomaticTrackingState` (Protobuf field number 1; repeated=False)<br>`design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `SetAutomaticTrackingStateResponse` | `set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 1; repeated=False) |
| `SetMonikerCompressionMethodRequest` | `method: ansys.api.discovery.v1.MonikerCompressionMethod` (Protobuf field number 1; repeated=False) |
| `SetMonikerCompressionMethodResponse` | `set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 1; repeated=False) |
| `TrackerDefinition` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `UndoRequest` | `steps: int32` (Protobuf field number 1; repeated=False) |
| `UndoResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `VersionIdentifier` | `major_release: int32` (Protobuf field number 1; repeated=False)<br>`minor_release: int32` (Protobuf field number 2; repeated=False)<br>`service_pack: int32` (Protobuf field number 3; repeated=False)<br>`build_number: int32` (Protobuf field number 4; repeated=False) |

### `ansys.api.discovery.v1.commands.communication_pb2`

| Message | Fields |
| --- | --- |
| `HealthRequest` | — |
| `HealthResponse` | `message: string` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `LogsRequest` | `target: ansys.api.discovery.v1.LogsTarget` (Protobuf field number 1; repeated=False)<br>`null_path: google.protobuf.NullValue` (Protobuf field number 2; repeated=False)<br>`target_path: string` (Protobuf field number 3; repeated=False)<br>`period_type: ansys.api.discovery.v1.LogsPeriodType` (Protobuf field number 4; repeated=False)<br>`null_period: google.protobuf.NullValue` (Protobuf field number 5; repeated=False)<br>`logs_period: google.protobuf.Timestamp` (Protobuf field number 6; repeated=False) |
| `LogsResponse` | `relative_path: string` (Protobuf field number 1; repeated=False)<br>`log_name: string` (Protobuf field number 2; repeated=False)<br>`log_chunk: bytes` (Protobuf field number 3; repeated=False) |
| `ShutdownRequest` | — |
| `ShutdownResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `StatusInfoRequest` | — |
| `StatusInfoResponse` | `touch_time: string` (Protobuf field number 1; repeated=False)<br>`application_version: string` (Protobuf field number 2; repeated=False)<br>`embedded_api_version: string` (Protobuf field number 3; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 4; repeated=False) |

### `ansys.api.discovery.v1.commands.file_pb2`

| Message | Fields |
| --- | --- |
| `CloseRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `CloseResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `GetReferencedDocumentsRequest` | `document_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetReferencedDocumentsResponse` | `response_data: ansys.api.discovery.v1.commands.file.GetReferencedDocumentsResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetReferencedDocumentsResponseData` | `data: bytes` (Protobuf field number 1; repeated=False)<br>`original_file_path: string` (Protobuf field number 2; repeated=False) |
| `ImportOptionDefinition` | `bool_option: bool` (Protobuf field number 1; repeated=False)<br>`string_option: string` (Protobuf field number 2; repeated=False) |
| `LoadAddinRequest` | `manifest_name: string` (Protobuf field number 1; repeated=False)<br>`data: bytes` (Protobuf field number 2; repeated=False) |
| `LoadAddinResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `NewRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `NewResponse` | `design: ansys.api.discovery.v1.design.designdoc.DesignDocEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `OpenFromUrlRequest` | `url_filepath: string` (Protobuf field number 1; repeated=False) |
| `OpenFromUrlResponse` | `design: ansys.api.discovery.v1.design.designdoc.DesignDocEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `OpenRequest` | `data: bytes` (Protobuf field number 1; repeated=False)<br>`file_name: string` (Protobuf field number 2; repeated=False)<br>`open_mode: ansys.api.discovery.v1.commands.file.OpenMode` (Protobuf field number 3; repeated=False)<br>`import_named_selections: bool` (Protobuf field number 4; repeated=False)<br>`import_options: ansys.api.discovery.v1.commands.file.OpenRequest.ImportOptionsEntry` (Protobuf field number 5; repeated=True)<br>`import_options_definitions: ansys.api.discovery.v1.commands.file.OpenRequest.ImportOptionsDefinitionsEntry` (Protobuf field number 6; repeated=True) |
| `OpenResponse` | `design: ansys.api.discovery.v1.design.designdoc.DesignDocEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `RunAddinMethodRequest` | `addin_name: string` (Protobuf field number 1; repeated=False)<br>`method_name: string` (Protobuf field number 2; repeated=False)<br>`arguments: google.protobuf.Any` (Protobuf field number 3; repeated=True) |
| `RunAddinMethodResponse` | `return_value: google.protobuf.Any` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SaveRequest` | `format: ansys.api.discovery.v1.FileFormat` (Protobuf field number 1; repeated=False)<br>`save_mode: ansys.api.discovery.v1.commands.file.SaveMode` (Protobuf field number 2; repeated=False)<br>`write_body_facets: bool` (Protobuf field number 3; repeated=False)<br>`parent_entity_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`file_name: string` (Protobuf field number 4; repeated=False)<br>`fmd_export_options: ansys.api.discovery.v1.design.FMDExportOptions` (Protobuf field number 8; repeated=False)<br>`pmdb_export_options: ansys.api.discovery.v1.design.PMDBExportOptions` (Protobuf field number 9; repeated=False) |
| `SaveResponse` | `data: bytes` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SaveToUrlRequest` | `save_mode: ansys.api.discovery.v1.commands.file.SaveMode` (Protobuf field number 1; repeated=False)<br>`write_body_facets: bool` (Protobuf field number 2; repeated=False) |
| `SaveToUrlResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.commands.historytrack_pb2`

| Message | Fields |
| --- | --- |
| `GetRecordingStatusRequest` | — |
| `GetRecordingStatusResponse` | `status: ansys.api.discovery.v1.commands.historytrack.RecordingStatus` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ReplayRequest` | — |
| `ReplayResponse` | `result: string` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetRecordingStatusRequest` | `status: ansys.api.discovery.v1.commands.historytrack.RecordingStatus` (Protobuf field number 1; repeated=False) |
| `SetRecordingStatusResponse` | `set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.commands.message_pb2`

| Message | Fields |
| --- | --- |
| `ClearRequest` | — |
| `ClearResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `GetMessageRequest` | — |
| `MessageResponse` | `event_message: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.commands.script_pb2`

| Message | Fields |
| --- | --- |
| `RecordingEventResponse` | `recording_string: string` (Protobuf field number 1; repeated=False) |
| `ReplayRequest` | — |
| `ReplayResponse` | `result: string` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `RunScriptFileRequest` | `script_path: string` (Protobuf field number 1; repeated=False)<br>`script_args: ansys.api.discovery.v1.commands.script.RunScriptFileRequest.ScriptArgsEntry` (Protobuf field number 2; repeated=True)<br>`api_version: int32` (Protobuf field number 3; repeated=False)<br>`script_type: ansys.api.discovery.v1.commands.script.RunScriptType` (Protobuf field number 4; repeated=False)<br>`data: bytes` (Protobuf field number 5; repeated=False) |
| `RunScriptFileResponse` | `values: ansys.api.discovery.v1.commands.script.RunScriptFileResponse.ValuesEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `RunScriptRequest` | `script: string` (Protobuf field number 1; repeated=False)<br>`api_version: int32` (Protobuf field number 2; repeated=False)<br>`script_args: ansys.api.discovery.v1.commands.script.RunScriptRequest.ScriptArgsEntry` (Protobuf field number 3; repeated=True) |
| `RunScriptResponse` | `script_result: bool` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False)<br>`values: ansys.api.discovery.v1.commands.script.RunScriptResponse.ValuesEntry` (Protobuf field number 3; repeated=True) |
| `SubscribeToRecordingRequest` | — |

### `ansys.api.discovery.v1.commands.unsupported_pb2`

| Message | Fields |
| --- | --- |
| `ByteArrayResponse` | `bytes: bytes` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ConvertToHeavyweightResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `CreateFacetedBodiesRequest` | `tessellation_data: ansys.api.discovery.v1.commands.unsupported.CreateFacetedBodiesRequest.TessellationDataEntry` (Protobuf field number 1; repeated=True) |
| `CreateFacetedBodiesResponse` | `created_bodies: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `ExportResultsToOpenVDBFileRequest` | `result_variables: ansys.api.discovery.v1.ResultVariable` (Protobuf field number 1; repeated=True)<br>`file_path: string` (Protobuf field number 2; repeated=False) |
| `ExportResultsToOpenVDBFileResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ExportResultsToOpenVDBMemoryRequest` | `result_variables: ansys.api.discovery.v1.ResultVariable` (Protobuf field number 1; repeated=True) |
| `ExportResultsToOpenVDBMemoryResponse` | `response: ansys.api.discovery.v1.commands.unsupported.ByteArrayResponse` (Protobuf field number 1; repeated=False) |
| `GetFacetedBodiesRequest` | `parts_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetFacetedBodiesResponse` | `faceted_bodies: ansys.api.discovery.v1.commands.unsupported.GetFacetedBodiesResponse.FacetedBodiesEntry` (Protobuf field number 1; repeated=True) |
| `GetImportIdMapRequest` | `type: ansys.api.discovery.v1.PersistentIdType` (Protobuf field number 1; repeated=False) |
| `GetImportIdMapResponse` | `id_map: ansys.api.discovery.v1.commands.unsupported.GetImportIdMapResponse.IdMapEntry` (Protobuf field number 1; repeated=True) |
| `GetLegendMaximumValueRequest` | — |
| `GetLegendMaximumValueResponse` | `response: double` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetLegendMinimumValueRequest` | — |
| `GetLegendMinimumValueResponse` | `response: double` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetSerializedSimulationObjectsRequest` | — |
| `GetSerializedSimulationObjectsResponse` | `simulation_objects: string` (Protobuf field number 1; repeated=False) |
| `GetSimulationContextRequest` | `include_monitors: bool` (Protobuf field number 1; repeated=False) |
| `GetSimulationContextResponse` | `simulation_context: string` (Protobuf field number 1; repeated=False) |
| `HasActiveSelectionRequest` | — |
| `HasActiveSelectionResponse` | `has_bodies: bool` (Protobuf field number 1; repeated=False)<br>`has_faces: bool` (Protobuf field number 2; repeated=False) |
| `RunCommandRequest` | `command: string` (Protobuf field number 1; repeated=False)<br>`data: string` (Protobuf field number 2; repeated=False) |
| `RunCommandResponse` | `data: string` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetExportIdData` | `moniker_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`id: string` (Protobuf field number 2; repeated=False)<br>`type: ansys.api.discovery.v1.PersistentIdType` (Protobuf field number 3; repeated=False) |
| `SetExportIdRequest` | `export_data: ansys.api.discovery.v1.commands.unsupported.SetExportIdData` (Protobuf field number 1; repeated=True) |
| `SetExportIdResponse` | — |
| `SetSoundEnabledResponse` | `success: bool` (Protobuf field number 1; repeated=False) |
| `SoundEnabledRequest` | `enabled: bool` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.commands.view_pb2`

| Message | Fields |
| --- | --- |
| `GetImageRequest` | `format: ansys.api.discovery.v1.ImageFormat` (Protobuf field number 1; repeated=False) |
| `GetImageResponse` | `data: bytes` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetViewRequest` | `view: ansys.api.discovery.v1.WindowView` (Protobuf field number 1; repeated=False) |
| `SetViewResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.commonmessages_pb2`

| Message | Fields |
| --- | --- |
| `AddTableQuantityPairRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.discovery.v1.QuantityPair` (Protobuf field number 2; repeated=False) |
| `Arc` | `center: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`start: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`end: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`axis: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False) |
| `ChangeQuantityPairRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.discovery.v1.QuantityPair` (Protobuf field number 2; repeated=False) |
| `Circle` | `center: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `CommandResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `CreationResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `DeleteResponse` | `deleted_object_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`failed_deletion_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`error_messages: string` (Protobuf field number 3; repeated=True) |
| `Direction` | `x: double` (Protobuf field number 1; repeated=False)<br>`y: double` (Protobuf field number 2; repeated=False)<br>`z: double` (Protobuf field number 3; repeated=False) |
| `EditTableQuantityPairRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`value: ansys.api.discovery.v1.QuantityPair` (Protobuf field number 2; repeated=False)<br>`row_index: int32` (Protobuf field number 3; repeated=False) |
| `Ellipse` | `center: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`majorradius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`minorradius: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `EntityIdentifier` | `id: string` (Protobuf field number 1; repeated=False) |
| `EntityRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `Frame` | `origin: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`dir_x: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`dir_y: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`dir_z: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False) |
| `GetBooleanResponse` | `value: bool` (Protobuf field number 1; repeated=False)<br>`get_data_response: ansys.api.discovery.v1.GetDataResponse` (Protobuf field number 2; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 3; repeated=False) |
| `GetByIdRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetByLabelRequest` | `label: string` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetDataResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `GuidEntityIdentifier` | `guid_as_string: string` (Protobuf field number 1; repeated=False) |
| `Line` | `start: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`end: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `MultipleEntitiesRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `OptionalInt` | `is_defined: bool` (Protobuf field number 1; repeated=False)<br>`number: int32` (Protobuf field number 2; repeated=False) |
| `OptionalQuantity` | `is_defined: bool` (Protobuf field number 1; repeated=False)<br>`quantity: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `OptionalVector` | `is_defined: bool` (Protobuf field number 1; repeated=False)<br>`vector: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 2; repeated=False) |
| `ParentEntityRequest` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `Plane` | `frame: ansys.api.discovery.v1.Frame` (Protobuf field number 1; repeated=False) |
| `Point` | `x: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`y: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`z: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `Polygon` | `center: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`numberofsides: int32` (Protobuf field number 3; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `Quantity` | `quantity_type: ansys.api.discovery.v1.QuantityType` (Protobuf field number 1; repeated=False)<br>`quantity_value: double` (Protobuf field number 2; repeated=False)<br>`unit: int32` (Protobuf field number 3; repeated=False)<br>`unit_abbreviation: string` (Protobuf field number 4; repeated=False)<br>`as_string: string` (Protobuf field number 5; repeated=False)<br>`value_in_geometry_units: double` (Protobuf field number 6; repeated=False) |
| `QuantityGenericTable` | `header: ansys.api.discovery.v1.TableHeader` (Protobuf field number 1; repeated=False)<br>`row_data: ansys.api.discovery.v1.QuantityGenericTableRow` (Protobuf field number 2; repeated=True) |
| `QuantityGenericTableRow` | `row_cells: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=True) |
| `QuantityPair` | `independant_data: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`dependant_data: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `QuantityPairTable` | `header: ansys.api.discovery.v1.TableHeader` (Protobuf field number 1; repeated=False)<br>`row_data: ansys.api.discovery.v1.QuantityPair` (Protobuf field number 2; repeated=True) |
| `QuantityVector` | `x: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`y: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`z: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `QuantityVectorTable` | `header: ansys.api.discovery.v1.TableHeader` (Protobuf field number 1; repeated=False)<br>`row_data: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 2; repeated=True) |
| `RayFireFaceImpact` | `face: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `RayFireFaceImpacts` | `impacts: ansys.api.discovery.v1.RayFireFaceImpact` (Protobuf field number 1; repeated=True) |
| `RayFireImpact` | `body: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `RayFireImpacts` | `impacts: ansys.api.discovery.v1.RayFireImpact` (Protobuf field number 1; repeated=True) |
| `RayFireUVImpact` | `body: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`u: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`v: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `RayFireUVImpacts` | `impacts: ansys.api.discovery.v1.RayFireUVImpact` (Protobuf field number 1; repeated=True) |
| `RemoveTableRowRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`row_index: int32` (Protobuf field number 2; repeated=False)<br>`independent_quantity: ansys.api.discovery.v1.QuantityType` (Protobuf field number 3; repeated=False) |
| `SetAssignmentRequest` | `referring_object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`referring_geometry_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`referenced_engineering_data_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 3; repeated=False)<br>`referenced_library_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 4; repeated=False) |
| `SetBooleanRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometry_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`boolean_value: bool` (Protobuf field number 3; repeated=False) |
| `SetIntRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`value: int32` (Protobuf field number 2; repeated=False) |
| `SetLocationExtendedRequest` | `set_location_request: ansys.api.discovery.v1.SetLocationRequest` (Protobuf field number 1; repeated=False)<br>`location_type: ansys.api.discovery.v1.LocationType` (Protobuf field number 2; repeated=False) |
| `SetLocationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`location_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `SetQuantityRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometry_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`quantity: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `SetQuantityVectorRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`quantity_vector: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 2; repeated=False) |
| `SetResponse` | `success: bool` (Protobuf field number 1; repeated=False)<br>`message: string` (Protobuf field number 2; repeated=False) |
| `SetStringRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`text_value: string` (Protobuf field number 2; repeated=False) |
| `SetUnitlessDoubleRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `TableHeader` | `table_name: string` (Protobuf field number 1; repeated=False)<br>`column_headers: string` (Protobuf field number 2; repeated=True)<br>`number_of_data_rows: int32` (Protobuf field number 3; repeated=False) |
| `TensorOfOptionalQuantities` | `dx: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 1; repeated=False)<br>`dy: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`dz: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 3; repeated=False)<br>`rx: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 4; repeated=False)<br>`ry: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 5; repeated=False)<br>`rz: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 6; repeated=False) |
| `VectorOfOptionalQuantities` | `x: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 1; repeated=False)<br>`y: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`z: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.design.constructs.coordinatesystem_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `request_data: ansys.api.discovery.v1.design.constructs.coordinatesystem.CreateRequestData` (Protobuf field number 1; repeated=True) |
| `CreateRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`frame: ansys.api.discovery.v1.Frame` (Protobuf field number 3; repeated=False) |
| `CreateResponse` | `coordinate_systems: ansys.api.discovery.v1.design.CoordinateSystemEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `coordinate_systems: ansys.api.discovery.v1.design.CoordinateSystemEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `coordinate_system: ansys.api.discovery.v1.design.CoordinateSystemEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetSuppressedRequest` | `coordinate_system_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SetSuppressedResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.constructs.datumline_pb2`

| Message | Fields |
| --- | --- |
| `DatumLineCreationRequest` | `request_data: ansys.api.discovery.v1.design.constructs.datumline.DatumLineCreationRequestData` (Protobuf field number 1; repeated=True) |
| `DatumLineCreationRequestData` | `line: ansys.api.discovery.v1.Line` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `DatumLineCreationResponse` | `lines: ansys.api.discovery.v1.design.DatumLineEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `lines: ansys.api.discovery.v1.design.DatumLineEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `line: ansys.api.discovery.v1.design.DatumLineEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.constructs.datumplane_pb2`

| Message | Fields |
| --- | --- |
| `DatumPlaneCreationRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`request_data: ansys.api.discovery.v1.design.constructs.datumplane.DatumPlaneCreationRequestData` (Protobuf field number 2; repeated=True) |
| `DatumPlaneCreationRequestData` | `plane: ansys.api.discovery.v1.Plane` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `DatumPlaneCreationResponse` | `planes: ansys.api.discovery.v1.design.DatumPlaneEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `planes: ansys.api.discovery.v1.design.DatumPlaneEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `plane: ansys.api.discovery.v1.design.DatumPlaneEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetSuppressedRequest` | `datum_plane_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SetSuppressedResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `UpdateStateResponse` | `update_states: ansys.api.discovery.v1.design.constructs.datumplane.UpdateStateResponse.UpdateStatesEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.constructs.datumpoint_pb2`

| Message | Fields |
| --- | --- |
| `DatumPointCreationRequest` | `request_data: ansys.api.discovery.v1.design.constructs.datumpoint.DatumPointCreationRequestData` (Protobuf field number 1; repeated=True) |
| `DatumPointCreationRequestData` | `points: ansys.api.discovery.v1.design.DatumPointEntity` (Protobuf field number 1; repeated=True)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `DatumPointCreationResponse` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `points: ansys.api.discovery.v1.design.DatumPointEntity` (Protobuf field number 1; repeated=True)<br>`get_data_response: ansys.api.discovery.v1.GetDataResponse` (Protobuf field number 2; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 3; repeated=False) |
| `GetPointResponse` | `point: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`get_data_response: ansys.api.discovery.v1.GetDataResponse` (Protobuf field number 2; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 3; repeated=False) |
| `GetResponse` | `point: ansys.api.discovery.v1.design.DatumPointEntity` (Protobuf field number 1; repeated=False)<br>`get_data_response: ansys.api.discovery.v1.GetDataResponse` (Protobuf field number 2; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.design.data.cadmaterial_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `request_data: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 1; repeated=True) |
| `CreateResponse` | `successfully_set: string` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `DeleteRequest` | `request_data: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 1; repeated=True) |
| `DeleteResponse` | `successfully_removed: string` (Protobuf field number 1; repeated=True)<br>`deletion_response: ansys.api.discovery.v1.design.data.cadmaterial.DeleteResponse` (Protobuf field number 2; repeated=False) |
| `GetAllNamesRequest` | — |
| `GetAllNamesResponse` | `materials: string` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.designdoc_pb2`

| Message | Fields |
| --- | --- |
| `CoordinateSystemList` | `coordinate_systems: ansys.api.discovery.v1.design.CoordinateSystemEntity` (Protobuf field number 1; repeated=True) |
| `DesignDocEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`is_complete: bool` (Protobuf field number 2; repeated=False)<br>`is_locked: bool` (Protobuf field number 3; repeated=False)<br>`is_modified: bool` (Protobuf field number 4; repeated=False)<br>`is_removed: bool` (Protobuf field number 5; repeated=False)<br>`main_part_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 6; repeated=False)<br>`main_part_displays_file_name: bool` (Protobuf field number 7; repeated=False)<br>`path: string` (Protobuf field number 10; repeated=False)<br>`name: string` (Protobuf field number 11; repeated=False) |
| `DesignTessellationRequest` | `options: ansys.api.discovery.v1.design.TessellationOptions` (Protobuf field number 1; repeated=False)<br>`include_faces: bool` (Protobuf field number 2; repeated=False)<br>`include_edges: bool` (Protobuf field number 3; repeated=False) |
| `DesignTessellationResponse` | `body_tessellation: ansys.api.discovery.v1.design.designdoc.DesignTessellationResponse.BodyTessellationEntry` (Protobuf field number 1; repeated=True) |
| `DesignTessellationResponseData` | `face_tessellation: ansys.api.discovery.v1.design.designdoc.DesignTessellationResponseData.FaceTessellationEntry` (Protobuf field number 1; repeated=True)<br>`edge_tessellation: ansys.api.discovery.v1.design.designdoc.DesignTessellationResponseData.EdgeTessellationEntry` (Protobuf field number 2; repeated=True) |
| `GetActiveRequest` | — |
| `GetActiveResponse` | `design: ansys.api.discovery.v1.design.designdoc.DesignDocEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `designs: ansys.api.discovery.v1.design.designdoc.DesignDocEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAsJsonRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetAsJsonResponse` | `json: string` (Protobuf field number 1; repeated=False) |
| `GetAssemblyRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetAssemblyResponse` | `parts: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 1; repeated=True)<br>`transformed_parts: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 2; repeated=True)<br>`components: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 3; repeated=True)<br>`bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 4; repeated=True)<br>`materials: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 5; repeated=True)<br>`named_selections: ansys.api.discovery.v1.design.NamedSelectionEntity` (Protobuf field number 6; repeated=True)<br>`component_coord_systems: ansys.api.discovery.v1.design.designdoc.GetAssemblyResponse.ComponentCoordSystemsEntry` (Protobuf field number 7; repeated=True)<br>`component_shared_topologies: ansys.api.discovery.v1.design.designdoc.GetAssemblyResponse.ComponentSharedTopologiesEntry` (Protobuf field number 8; repeated=True)<br>`beams: ansys.api.discovery.v1.design.BeamEntity` (Protobuf field number 9; repeated=True)<br>`design_points: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 10; repeated=True)<br>`driving_dimensions: ansys.api.discovery.v1.design.DrivingDimensionEntity` (Protobuf field number 11; repeated=True)<br>`datum_planes: ansys.api.discovery.v1.design.DatumPlaneEntity` (Protobuf field number 12; repeated=True)<br>`datum_points: ansys.api.discovery.v1.design.DatumPointEntity` (Protobuf field number 13; repeated=True)<br>`datum_lines: ansys.api.discovery.v1.design.DatumLineEntity` (Protobuf field number 14; repeated=True) |
| `GetGeometryUnitsRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetGeometryUnitsResponse` | `units: ansys.api.discovery.v1.design.designdoc.GeometryUnits` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `design: ansys.api.discovery.v1.design.designdoc.DesignDocEntity` (Protobuf field number 1; repeated=False) |
| `SetActiveRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `SetActiveResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `SetGeometryUnitsRequest` | `design_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`units: ansys.api.discovery.v1.design.designdoc.GeometryUnits` (Protobuf field number 2; repeated=False) |
| `SetGeometryUnitsResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.design.designmessages_pb2`

| Message | Fields |
| --- | --- |
| `AlignCondition` | `condition: ansys.api.discovery.v1.design.MatingCondition` (Protobuf field number 1; repeated=False)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `AnchorCondition` | `condition: ansys.api.discovery.v1.design.MatingCondition` (Protobuf field number 1; repeated=False)<br>`component: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 2; repeated=False) |
| `BeamEntity` | `name: string` (Protobuf field number 1; repeated=False)<br>`can_suppress: bool` (Protobuf field number 2; repeated=False)<br>`is_deleted: bool` (Protobuf field number 3; repeated=False)<br>`is_reversed: bool` (Protobuf field number 4; repeated=False)<br>`is_rigid: bool` (Protobuf field number 5; repeated=False)<br>`material: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 6; repeated=False)<br>`id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`parent: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 8; repeated=False)<br>`cross_section: ansys.api.discovery.v1.design.ProfileCrossSectionInfo` (Protobuf field number 9; repeated=False)<br>`properties: ansys.api.discovery.v1.design.ProfileProperties` (Protobuf field number 10; repeated=False)<br>`shape: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 11; repeated=False)<br>`type: ansys.api.discovery.v1.BeamType` (Protobuf field number 12; repeated=False) |
| `BodyEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`can_suppress: bool` (Protobuf field number 3; repeated=False)<br>`is_deleted: bool` (Protobuf field number 4; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 5; repeated=False)<br>`transform_to_master: ansys.api.discovery.v1.design.Matrix` (Protobuf field number 6; repeated=False)<br>`master: ansys.api.discovery.v1.design.BodyMasterNullable` (Protobuf field number 7; repeated=False)<br>`master_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 8; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 9; repeated=False)<br>`is_surface: bool` (Protobuf field number 10; repeated=False)<br>`is_lightweight: bool` (Protobuf field number 11; repeated=False) |
| `BodyMaster` | `update_state: string` (Protobuf field number 6; repeated=False)<br>`text_attributes: ansys.api.discovery.v1.design.BodyMaster.TextAttributesEntry` (Protobuf field number 7; repeated=True)<br>`number_attributes: ansys.api.discovery.v1.design.BodyMaster.NumberAttributesEntry` (Protobuf field number 8; repeated=True)<br>`material: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 9; repeated=False)<br>`surface_material: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 10; repeated=False)<br>`shape: ansys.api.discovery.v1.design.Shape` (Protobuf field number 11; repeated=False) |
| `BodyMasterNullable` | `null: google.protobuf.NullValue` (Protobuf field number 1; repeated=False)<br>`props: ansys.api.discovery.v1.design.BodyMaster` (Protobuf field number 2; repeated=False) |
| `BoltEntity` | `name: string` (Protobuf field number 1; repeated=False)<br>`can_suppress: bool` (Protobuf field number 2; repeated=False)<br>`is_deleted: bool` (Protobuf field number 3; repeated=False)<br>`id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=False)<br>`parent: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 5; repeated=False) |
| `Box` | `min: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`center: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False) |
| `ComponentEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`part_occurrence: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 3; repeated=False)<br>`placement: ansys.api.discovery.v1.design.Matrix` (Protobuf field number 4; repeated=False)<br>`master_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 6; repeated=False)<br>`part_master: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 7; repeated=False)<br>`display_name: string` (Protobuf field number 8; repeated=False)<br>`instance_name: string` (Protobuf field number 9; repeated=False)<br>`template_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 10; repeated=False) |
| `ControlPoint` | `position: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`weight: double` (Protobuf field number 2; repeated=False) |
| `CoordinateSystemEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`frame: ansys.api.discovery.v1.Frame` (Protobuf field number 3; repeated=False) |
| `CurveEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`owner_name: string` (Protobuf field number 2; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`points: ansys.api.discovery.v1.Point` (Protobuf field number 4; repeated=True)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`geometry: ansys.api.discovery.v1.design.CurveGeometry` (Protobuf field number 6; repeated=False) |
| `CurveEvaluation` | `curvature: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`derivative: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`derivative2: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`param: double` (Protobuf field number 4; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 5; repeated=False)<br>`tangent: ansys.api.discovery.v1.Direction` (Protobuf field number 6; repeated=False) |
| `CurveGeometry` | `origin: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`major_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`minor_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 5; repeated=False)<br>`reference: ansys.api.discovery.v1.Direction` (Protobuf field number 6; repeated=False)<br>`axis: ansys.api.discovery.v1.Direction` (Protobuf field number 7; repeated=False)<br>`nurbs_curve: ansys.api.discovery.v1.design.NurbsCurve` (Protobuf field number 8; repeated=False) |
| `DatumLineEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`line: ansys.api.discovery.v1.design.CurveGeometry` (Protobuf field number 3; repeated=False)<br>`is_deleted: bool` (Protobuf field number 4; repeated=False)<br>`master_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 6; repeated=False)<br>`is_pinned: bool` (Protobuf field number 7; repeated=False) |
| `DatumPlaneEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 4; repeated=False)<br>`is_deleted: bool` (Protobuf field number 5; repeated=False)<br>`can_suppress: bool` (Protobuf field number 6; repeated=False)<br>`master_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 8; repeated=False)<br>`curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 9; repeated=True) |
| `DatumPointEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`position: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 4; repeated=False)<br>`is_deleted: bool` (Protobuf field number 5; repeated=False)<br>`can_suppress: bool` (Protobuf field number 6; repeated=False)<br>`master_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 8; repeated=False)<br>`is_pinned: bool` (Protobuf field number 9; repeated=False) |
| `DrivingDimensionEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`dimension_type: ansys.api.discovery.v1.DimensionType` (Protobuf field number 3; repeated=False)<br>`dimension_value: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `EdgeEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 2; repeated=False)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 10; repeated=False)<br>`owner_name: string` (Protobuf field number 11; repeated=False)<br>`export_id: string` (Protobuf field number 12; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 13; repeated=False)<br>`owner_id: string` (Protobuf field number 14; repeated=False)<br>`is_reversed: bool` (Protobuf field number 15; repeated=False) |
| `EdgeTessellation` | `vertices: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=True) |
| `EntitiesCollection` | `curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 1; repeated=True)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True)<br>`faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 3; repeated=True)<br>`bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 4; repeated=True) |
| `FMDExportOptions` | `deviation: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`aspect_ratio: int32` (Protobuf field number 3; repeated=False)<br>`max_edge_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `FaceEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 2; repeated=False)<br>`surface_type: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 10; repeated=False)<br>`owner_name: string` (Protobuf field number 11; repeated=False)<br>`export_id: string` (Protobuf field number 12; repeated=False)<br>`area: ansys.api.discovery.v1.Quantity` (Protobuf field number 13; repeated=False)<br>`is_reversed: bool` (Protobuf field number 14; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 15; repeated=False) |
| `FilletWeldEntity` | `geometry: ansys.api.discovery.v1.design.TrimmedCurveList` (Protobuf field number 1; repeated=True)<br>`display_name: string` (Protobuf field number 2; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`volume: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`mass: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`time: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`rod_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`is_intermittent: bool` (Protobuf field number 8; repeated=False)<br>`sequence_id: int32` (Protobuf field number 9; repeated=False)<br>`size1: ansys.api.discovery.v1.Quantity` (Protobuf field number 10; repeated=False)<br>`size2: ansys.api.discovery.v1.Quantity` (Protobuf field number 11; repeated=False)<br>`is_angular: bool` (Protobuf field number 12; repeated=False)<br>`is_at_center: bool` (Protobuf field number 13; repeated=False)<br>`intermittent_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 14; repeated=False)<br>`number_of_welds: int32` (Protobuf field number 15; repeated=False)<br>`pitch: ansys.api.discovery.v1.Quantity` (Protobuf field number 16; repeated=False)<br>`trajectory_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 17; repeated=False)<br>`number_of_sides: int32` (Protobuf field number 18; repeated=False)<br>`all_around: bool` (Protobuf field number 19; repeated=False) |
| `GearCondition` | `condition: ansys.api.discovery.v1.design.MatingCondition` (Protobuf field number 1; repeated=False)<br>`is_belt: bool` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `Geometries` | `points: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=True)<br>`lines: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=True)<br>`arcs: ansys.api.discovery.v1.Arc` (Protobuf field number 3; repeated=True)<br>`circles: ansys.api.discovery.v1.Circle` (Protobuf field number 4; repeated=True)<br>`ellipses: ansys.api.discovery.v1.Ellipse` (Protobuf field number 5; repeated=True)<br>`polygons: ansys.api.discovery.v1.Polygon` (Protobuf field number 6; repeated=True)<br>`nurbs_curves: ansys.api.discovery.v1.design.NurbsCurve` (Protobuf field number 7; repeated=True) |
| `GetBoundingBoxRequest` | `request_data: ansys.api.discovery.v1.design.GetBoundingBoxRequestData` (Protobuf field number 1; repeated=True) |
| `GetBoundingBoxRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 2; repeated=False) |
| `GetBoundingBoxResponse` | `response_data: ansys.api.discovery.v1.design.GetBoundingBoxResponseData` (Protobuf field number 1; repeated=True) |
| `GetBoundingBoxResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`box: ansys.api.discovery.v1.design.Box` (Protobuf field number 2; repeated=False) |
| `GetCentroidResponse` | `response_data: ansys.api.discovery.v1.design.GetCentroidResponseData` (Protobuf field number 1; repeated=True) |
| `GetCentroidResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`centroid: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `GetColorResponse` | `colors: ansys.api.discovery.v1.design.GetColorResponse.ColorsEntry` (Protobuf field number 1; repeated=True) |
| `GetFacesResponse` | `response_data: ansys.api.discovery.v1.design.GetFacesResponseData` (Protobuf field number 1; repeated=True) |
| `GetFacesResponseData` | `associated_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 2; repeated=True) |
| `GetIsDeletedResponse` | `deleted: ansys.api.discovery.v1.design.GetIsDeletedResponse.DeletedEntry` (Protobuf field number 1; repeated=True) |
| `GetUpdateStateResponse` | `update_states: ansys.api.discovery.v1.design.GetUpdateStateResponse.UpdateStatesEntry` (Protobuf field number 1; repeated=True) |
| `Knot` | `multiplicity: int32` (Protobuf field number 1; repeated=False)<br>`parameter: double` (Protobuf field number 2; repeated=False) |
| `Loop` | `type: string` (Protobuf field number 1; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`bounding_box: ansys.api.discovery.v1.design.Box` (Protobuf field number 3; repeated=False)<br>`edges: string` (Protobuf field number 4; repeated=True) |
| `MaterialEntity` | `name: string` (Protobuf field number 1; repeated=False)<br>`material_properties: ansys.api.discovery.v1.design.MaterialProperty` (Protobuf field number 2; repeated=True) |
| `MaterialProperty` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`display_name: string` (Protobuf field number 2; repeated=False)<br>`value: double` (Protobuf field number 3; repeated=False)<br>`units: string` (Protobuf field number 4; repeated=False) |
| `MatingCondition` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`is_deleted: bool` (Protobuf field number 2; repeated=False)<br>`is_enabled: bool` (Protobuf field number 3; repeated=False)<br>`is_satisfied: bool` (Protobuf field number 4; repeated=False) |
| `Matrix` | `m00: double` (Protobuf field number 1; repeated=False)<br>`m01: double` (Protobuf field number 2; repeated=False)<br>`m02: double` (Protobuf field number 3; repeated=False)<br>`m03: double` (Protobuf field number 4; repeated=False)<br>`m10: double` (Protobuf field number 5; repeated=False)<br>`m11: double` (Protobuf field number 6; repeated=False)<br>`m12: double` (Protobuf field number 7; repeated=False)<br>`m13: double` (Protobuf field number 8; repeated=False)<br>`m20: double` (Protobuf field number 9; repeated=False)<br>`m21: double` (Protobuf field number 10; repeated=False)<br>`m22: double` (Protobuf field number 11; repeated=False)<br>`m23: double` (Protobuf field number 12; repeated=False)<br>`m30: double` (Protobuf field number 13; repeated=False)<br>`m31: double` (Protobuf field number 14; repeated=False)<br>`m32: double` (Protobuf field number 15; repeated=False)<br>`m33: double` (Protobuf field number 16; repeated=False) |
| `MeshEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `NamedSelectionEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=True)<br>`bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 4; repeated=True)<br>`faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 5; repeated=True)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 6; repeated=True)<br>`beams: ansys.api.discovery.v1.design.BeamEntity` (Protobuf field number 7; repeated=True)<br>`design_points: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 8; repeated=True)<br>`vertices: ansys.api.discovery.v1.design.Vertex` (Protobuf field number 9; repeated=True)<br>`components: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 10; repeated=True)<br>`curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 11; repeated=True)<br>`datum_planes: ansys.api.discovery.v1.design.DatumPlaneEntity` (Protobuf field number 12; repeated=True)<br>`coordinate_systems: ansys.api.discovery.v1.design.CoordinateSystemEntity` (Protobuf field number 13; repeated=True)<br>`datum_points: ansys.api.discovery.v1.design.DatumPointEntity` (Protobuf field number 14; repeated=True)<br>`datum_lines: ansys.api.discovery.v1.design.DatumLineEntity` (Protobuf field number 15; repeated=True) |
| `NurbsCurve` | `control_points: ansys.api.discovery.v1.design.ControlPoint` (Protobuf field number 1; repeated=True)<br>`nurbs_data: ansys.api.discovery.v1.design.NurbsData` (Protobuf field number 2; repeated=False)<br>`is_rational: bool` (Protobuf field number 3; repeated=False)<br>`parameterization: ansys.api.discovery.v1.design.Parameterization` (Protobuf field number 4; repeated=False) |
| `NurbsData` | `degree: int32` (Protobuf field number 1; repeated=False)<br>`is_closed: bool` (Protobuf field number 2; repeated=False)<br>`is_periodic: bool` (Protobuf field number 3; repeated=False)<br>`knots: ansys.api.discovery.v1.design.Knot` (Protobuf field number 4; repeated=True)<br>`order: int32` (Protobuf field number 5; repeated=False) |
| `NurbsSurface` | `control_points: ansys.api.discovery.v1.design.ControlPoint` (Protobuf field number 1; repeated=True)<br>`nurbs_data_u: ansys.api.discovery.v1.design.NurbsData` (Protobuf field number 2; repeated=False)<br>`nurbs_data_v: ansys.api.discovery.v1.design.NurbsData` (Protobuf field number 3; repeated=False)<br>`is_rational: bool` (Protobuf field number 4; repeated=False)<br>`parameterization_u: ansys.api.discovery.v1.design.Parameterization` (Protobuf field number 5; repeated=False)<br>`parameterization_v: ansys.api.discovery.v1.design.Parameterization` (Protobuf field number 6; repeated=False) |
| `OrientCondition` | `condition: ansys.api.discovery.v1.design.MatingCondition` (Protobuf field number 1; repeated=False)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `PMDBExportOptions` | `parameter_prefixes: string` (Protobuf field number 1; repeated=False)<br>`cad_attribute_prefixes: string` (Protobuf field number 2; repeated=False)<br>`named_selection_prefixes: string` (Protobuf field number 3; repeated=False)<br>`analysis_type: ansys.api.discovery.v1.PMDBAnalysisType` (Protobuf field number 4; repeated=False)<br>`mixed_part_export_type: ansys.api.discovery.v1.PMDBMixedPartExportType` (Protobuf field number 5; repeated=False)<br>`attach_flattened_assembly: bool` (Protobuf field number 6; repeated=False)<br>`use_cad_mass_properties: bool` (Protobuf field number 7; repeated=False)<br>`plane_prefixes: string` (Protobuf field number 8; repeated=False)<br>`coordinate_system_prefixes: string` (Protobuf field number 9; repeated=False)<br>`advanced_geom_processing: bool` (Protobuf field number 10; repeated=False)<br>`angular_deviation: double` (Protobuf field number 11; repeated=False)<br>`attach_weight_class: ansys.api.discovery.v1.PMDBAttachWeightClass` (Protobuf field number 12; repeated=False)<br>`cad_associativity: bool` (Protobuf field number 13; repeated=False)<br>`cad_attribute_transfer: bool` (Protobuf field number 14; repeated=False)<br>`do_smart_update: bool` (Protobuf field number 15; repeated=False)<br>`geometry_deviation: double` (Protobuf field number 16; repeated=False)<br>`process_coordinate_sys: bool` (Protobuf field number 17; repeated=False)<br>`process_planes: bool` (Protobuf field number 18; repeated=False)<br>`import_using_instances: bool` (Protobuf field number 19; repeated=False)<br>`process_work_points: bool` (Protobuf field number 20; repeated=False)<br>`is_selective_update: bool` (Protobuf field number 21; repeated=False)<br>`material_properties: bool` (Protobuf field number 22; repeated=False)<br>`granta_material_properties: bool` (Protobuf field number 23; repeated=False)<br>`max_facet_size: double` (Protobuf field number 24; repeated=False)<br>`named_selection: bool` (Protobuf field number 25; repeated=False)<br>`parameter_processing_type: ansys.api.discovery.v1.PMDBParameterType` (Protobuf field number 26; repeated=False)<br>`plug_in_facet_quality: ansys.api.discovery.v1.PMDBPlugInFacetQuality` (Protobuf field number 27; repeated=False)<br>`process_enclosure_and_symmetry: bool` (Protobuf field number 28; repeated=False)<br>`reader_save_part: bool` (Protobuf field number 29; repeated=False)<br>`target_application: ansys.api.discovery.v1.PMDBTargetApplication` (Protobuf field number 30; repeated=False)<br>`temp_directory: string` (Protobuf field number 31; repeated=False)<br>`process_physics_definition: bool` (Protobuf field number 32; repeated=False)<br>`process_solid_bodies: bool` (Protobuf field number 33; repeated=False)<br>`process_surface_bodies: bool` (Protobuf field number 34; repeated=False)<br>`process_line_bodies: bool` (Protobuf field number 35; repeated=False) |
| `Parameterization` | `bounds: ansys.api.discovery.v1.design.ParameterizationBounds` (Protobuf field number 1; repeated=False)<br>`form: ansys.api.discovery.v1.ParameterizationForm` (Protobuf field number 2; repeated=False) |
| `ParameterizationBounds` | `infinite_start: bool` (Protobuf field number 1; repeated=False)<br>`start: double` (Protobuf field number 2; repeated=False)<br>`infinite_end: bool` (Protobuf field number 3; repeated=False)<br>`end: double` (Protobuf field number 4; repeated=False) |
| `PartEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `ProfileCrossSectionInfo` | `section_anchor: int32` (Protobuf field number 1; repeated=False)<br>`section_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`section_frame: ansys.api.discovery.v1.Frame` (Protobuf field number 3; repeated=False)<br>`section_profile: ansys.api.discovery.v1.design.TrimmedCurveList` (Protobuf field number 4; repeated=True) |
| `ProfileProperties` | `area: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`centroid_x: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`centroid_y: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`warping_constant: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`ixx: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`ixy: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`iyy: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`torsional_constant: ansys.api.discovery.v1.Quantity` (Protobuf field number 8; repeated=False)<br>`shear_center_x: ansys.api.discovery.v1.Quantity` (Protobuf field number 9; repeated=False)<br>`shear_center_y: ansys.api.discovery.v1.Quantity` (Protobuf field number 10; repeated=False) |
| `RigidCondition` | `condition: ansys.api.discovery.v1.design.MatingCondition` (Protobuf field number 1; repeated=False)<br>`component_a: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 2; repeated=False)<br>`component_b: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 3; repeated=False) |
| `Separation` | `distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`point_a: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`point_b: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False) |
| `SetColorRequest` | `request_data: ansys.api.discovery.v1.design.SetColorRequestData` (Protobuf field number 1; repeated=True) |
| `SetColorRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`color: string` (Protobuf field number 2; repeated=False) |
| `SetColorResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `SetDesignEntityNameRequest` | `request_data: ansys.api.discovery.v1.design.SetDesignEntityNameRequestData` (Protobuf field number 1; repeated=True) |
| `SetDesignEntityNameRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False) |
| `SetDesignEntityNameResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `Shape` | `is_surface_body: bool` (Protobuf field number 1; repeated=False)<br>`surface_area: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`volume: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`bounding_box_size: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False) |
| `SpotWeldEntity` | `weld_points: ansys.api.discovery.v1.design.SpotWeldEntity.WeldPointsEntry` (Protobuf field number 1; repeated=True) |
| `Surface` | `origin: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`half_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`major_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`minor_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`reference: ansys.api.discovery.v1.Direction` (Protobuf field number 6; repeated=False)<br>`axis: ansys.api.discovery.v1.Direction` (Protobuf field number 7; repeated=False)<br>`nurbs_surface: ansys.api.discovery.v1.design.NurbsSurface` (Protobuf field number 8; repeated=False) |
| `SurfaceEvaluation` | `derivative_u: ansys.api.discovery.v1.Direction` (Protobuf field number 1; repeated=False)<br>`derivative_uu: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`derivative_uv: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`derivative_v: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False)<br>`derivative_vv: ansys.api.discovery.v1.Direction` (Protobuf field number 5; repeated=False)<br>`max_curvature: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`max_curvature_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 7; repeated=False)<br>`min_curvature: ansys.api.discovery.v1.Quantity` (Protobuf field number 8; repeated=False)<br>`min_curvature_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 9; repeated=False)<br>`normal: ansys.api.discovery.v1.Direction` (Protobuf field number 10; repeated=False)<br>`param_u: ansys.api.discovery.v1.Quantity` (Protobuf field number 11; repeated=False)<br>`param_v: ansys.api.discovery.v1.Quantity` (Protobuf field number 12; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 13; repeated=False) |
| `TangentCondition` | `condition: ansys.api.discovery.v1.design.MatingCondition` (Protobuf field number 1; repeated=False)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`is_reversed: bool` (Protobuf field number 3; repeated=False)<br>`is_valid: bool` (Protobuf field number 4; repeated=False) |
| `Tessellation` | `vertices: double` (Protobuf field number 1; repeated=True)<br>`faces: int32` (Protobuf field number 2; repeated=True)<br>`facecolor: int32` (Protobuf field number 3; repeated=False) |
| `TessellationOptions` | `surface_deviation: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`angle_deviation: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`maximum_aspect_ratio: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`maximum_edge_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`watertight: bool` (Protobuf field number 5; repeated=False)<br>`curve_deviation: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `TrackedChanges` | `created_bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`modified_bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 2; repeated=True)<br>`deleted_body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=True)<br>`created_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`modified_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=True)<br>`deleted_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 6; repeated=True)<br>`created_edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=True)<br>`modified_edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 8; repeated=True)<br>`deleted_edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 9; repeated=True)<br>`created_components: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 10; repeated=True)<br>`modified_components: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 11; repeated=True)<br>`deleted_component_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 12; repeated=True)<br>`created_parts: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 13; repeated=True)<br>`modified_parts: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 14; repeated=True)<br>`deleted_part_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 15; repeated=True) |
| `TrackedCommandResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 2; repeated=False) |
| `TrackedCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 2; repeated=False) |
| `TrackedDeleteResponse` | `delete_response: ansys.api.discovery.v1.DeleteResponse` (Protobuf field number 1; repeated=False)<br>`tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 2; repeated=False) |
| `TrackedSetResponse` | `set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 1; repeated=False)<br>`tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 2; repeated=False) |
| `TrimmedCurve` | `curve: ansys.api.discovery.v1.design.CurveGeometry` (Protobuf field number 1; repeated=False)<br>`start: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`end: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`interval_start: double` (Protobuf field number 4; repeated=False)<br>`interval_end: double` (Protobuf field number 5; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `TrimmedCurveList` | `curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 1; repeated=True) |
| `TrimmedSurface` | `surface: ansys.api.discovery.v1.design.Surface` (Protobuf field number 1; repeated=False)<br>`type: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 2; repeated=False)<br>`u_min: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`u_max: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`v_min: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`v_max: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `UpdateState` | `state: int32` (Protobuf field number 1; repeated=False) |
| `Vertex` | `position: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True)<br>`id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `WeldEntity` | `geometry: ansys.api.discovery.v1.design.TrimmedCurveList` (Protobuf field number 1; repeated=True)<br>`display_name: string` (Protobuf field number 2; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`volume: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`mass: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`time: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`rod_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`is_intermittent: bool` (Protobuf field number 8; repeated=False)<br>`sequence_id: int32` (Protobuf field number 9; repeated=False)<br>`size1: ansys.api.discovery.v1.Quantity` (Protobuf field number 10; repeated=False)<br>`size2: ansys.api.discovery.v1.Quantity` (Protobuf field number 11; repeated=False)<br>`is_angular: bool` (Protobuf field number 12; repeated=False)<br>`is_at_center: bool` (Protobuf field number 13; repeated=False)<br>`intermittent_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 14; repeated=False)<br>`number_of_welds: int32` (Protobuf field number 15; repeated=False)<br>`pitch: ansys.api.discovery.v1.Quantity` (Protobuf field number 16; repeated=False) |

### `ansys.api.discovery.v1.design.extensions.beam_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `beam_entities: ansys.api.discovery.v1.design.BeamEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `beam_data: ansys.api.discovery.v1.design.BeamEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetBeamAnchorPositionRequest` | `geometry_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`anchor_position: ansys.api.discovery.v1.BeamAnchorPosition` (Protobuf field number 2; repeated=False) |
| `SetBeamTreatAsRequest` | `geometry_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`treat_as: ansys.api.discovery.v1.BeamType` (Protobuf field number 2; repeated=False) |
| `SetSuppressedRequest` | `beam_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SetSuppressedResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.extensions.bolt_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `bolt_entities: ansys.api.discovery.v1.design.BoltEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `bolt_data: ansys.api.discovery.v1.design.BoltEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.extensions.weld_pb2`

| Message | Fields |
| --- | --- |
| `GetAllFilletWeldsRequest` | — |
| `GetAllFilletWeldsResponse` | `weld_entities: ansys.api.discovery.v1.design.FilletWeldEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `weld_entities: ansys.api.discovery.v1.design.WeldEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAllSpotWeldsRequest` | — |
| `GetAllSpotWeldsResponse` | `welds: ansys.api.discovery.v1.design.SpotWeldEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `weld_data: ansys.api.discovery.v1.design.WeldEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.geometry.body_pb2`

| Message | Fields |
| --- | --- |
| `BodiesSelectionResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True) |
| `CopyFacesRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CopyFacesRequestData` (Protobuf field number 1; repeated=True) |
| `CopyFacesRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `CopyFacesResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateBlockBodyRequest` | `start_point: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`end_point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=False) |
| `CreateBlockBodyResponse` | `body: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=False)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateBodyFromFaceRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateBodyFromFaceRequestData` (Protobuf field number 1; repeated=True) |
| `CreateBodyFromFaceRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`face_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateBodyFromFaceResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateBodyFromLoftWithGuidesRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateBodyFromLoftWithGuidesRequestData` (Protobuf field number 1; repeated=True) |
| `CreateBodyFromLoftWithGuidesRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`profiles: ansys.api.discovery.v1.design.TrimmedCurveList` (Protobuf field number 3; repeated=True)<br>`guides: ansys.api.discovery.v1.design.TrimmedCurveList` (Protobuf field number 6; repeated=False) |
| `CreateBodyFromLoftWithGuidesResponse` | `created_bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateDuplicateBodyRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.DuplicateBodyRequestData` (Protobuf field number 1; repeated=True) |
| `CreateDuplicateBodyResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.DuplicateBodyResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_creation_response: ansys.api.discovery.v1.design.TrackedCreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateExtrudedBodyFromFaceProfileRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyFromFaceProfileRequestData` (Protobuf field number 1; repeated=True) |
| `CreateExtrudedBodyFromFaceProfileRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`face_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `CreateExtrudedBodyFromFaceProfileResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateExtrudedBodyFromLoftProfilesRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyFromLoftProfilesRequestData` (Protobuf field number 1; repeated=True) |
| `CreateExtrudedBodyFromLoftProfilesRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`profiles: ansys.api.discovery.v1.design.TrimmedCurveList` (Protobuf field number 3; repeated=True)<br>`periodic: bool` (Protobuf field number 4; repeated=False)<br>`ruled: bool` (Protobuf field number 5; repeated=False) |
| `CreateExtrudedBodyFromLoftProfilesResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateExtrudedBodyRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateExtrudedBodyRequestData` (Protobuf field number 1; repeated=True) |
| `CreateExtrudedBodyRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 4; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `CreateExtrudedBodyResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreatePlanarBodyRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreatePlanarBodyRequestData` (Protobuf field number 1; repeated=True) |
| `CreatePlanarBodyRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 4; repeated=False) |
| `CreatePlanarBodyResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateSphereBodyRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateSphereBodyRequestData` (Protobuf field number 1; repeated=True) |
| `CreateSphereBodyRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`center: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `CreateSphereBodyResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateSurfaceBodyFromTrimmedCurvesRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateSurfaceBodyFromTrimmedCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `CreateSurfaceBodyFromTrimmedCurvesRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`trimmed_curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 3; repeated=True) |
| `CreateSurfaceBodyFromTrimmedCurvesResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateSurfaceBodyRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateSurfaceBodyRequestData` (Protobuf field number 1; repeated=True) |
| `CreateSurfaceBodyRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`trimmed_surface: ansys.api.discovery.v1.design.TrimmedSurface` (Protobuf field number 3; repeated=False) |
| `CreateSurfaceBodyResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateSweepingChainRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateSweepingChainRequestData` (Protobuf field number 1; repeated=True) |
| `CreateSweepingChainRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`chain: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 3; repeated=True)<br>`path: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 4; repeated=True) |
| `CreateSweepingChainResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateSweepingProfileRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateSweepingProfileRequestData` (Protobuf field number 1; repeated=True) |
| `CreateSweepingProfileRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 4; repeated=False)<br>`path: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 5; repeated=True) |
| `CreateSweepingProfileResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateTorusRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.CreateTorusRequestData` (Protobuf field number 1; repeated=True) |
| `CreateTorusRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`major_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`minor_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`frame: ansys.api.discovery.v1.Frame` (Protobuf field number 5; repeated=False) |
| `CreateTorusResponse` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_creation_response: ansys.api.discovery.v1.design.TrackedCreationResponse` (Protobuf field number 2; repeated=False) |
| `DuplicateBodyRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `DuplicateBodyResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `bodies: ansys.api.discovery.v1.design.geometry.body.BodiesSelectionResponse` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAssignedCADMaterialResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetAssignedCADMaterialResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAssignedCADMaterialResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`material: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 2; repeated=False) |
| `GetBodyRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_type: ansys.api.discovery.v1.BodyType` (Protobuf field number 2; repeated=False) |
| `GetBodyResponse` | `body: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetClosestSeparationRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.GetClosestSeparationRequestData` (Protobuf field number 1; repeated=True) |
| `GetClosestSeparationRequestData` | `body_1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_2_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetClosestSeparationResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetClosestSeparationResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `GetClosestSeparationResponseData` | `body_1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_2_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`separation: ansys.api.discovery.v1.design.Separation` (Protobuf field number 3; repeated=False) |
| `GetCollisionRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.GetCollisionRequestData` (Protobuf field number 1; repeated=True) |
| `GetCollisionRequestData` | `body_1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_2_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetCollisionResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetCollisionResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetCollisionResponseData` | `body_1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_2_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`collision: ansys.api.discovery.v1.CollisionType` (Protobuf field number 3; repeated=False) |
| `GetEdgesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetEdgesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetEdgesResponseData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True) |
| `GetFillStyleResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetFillStyleResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetFillStyleResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`fill_style: ansys.api.discovery.v1.BodyFillStyle` (Protobuf field number 2; repeated=False) |
| `GetIsEnclosureBodyResponse` | `result: ansys.api.discovery.v1.design.geometry.body.GetIsEnclosureBodyResponse.ResultEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetIsSuppressedResponse` | `result: ansys.api.discovery.v1.design.geometry.body.GetIsSuppressedResponse.ResultEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetNameResponse` | `names: ansys.api.discovery.v1.design.geometry.body.GetNameResponse.NamesEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetSurfaceBodyThicknessResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetSurfaceBodyThicknessResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetSurfaceBodyThicknessResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`result: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetTessellationRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.GetTessellationRequestData` (Protobuf field number 1; repeated=True) |
| `GetTessellationRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`options: ansys.api.discovery.v1.design.TessellationOptions` (Protobuf field number 2; repeated=False)<br>`include_faces: bool` (Protobuf field number 3; repeated=False)<br>`include_edges: bool` (Protobuf field number 4; repeated=False) |
| `GetTessellationResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetTessellationResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetTessellationResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`face_tessellation: ansys.api.discovery.v1.design.geometry.body.GetTessellationResponseData.FaceTessellationEntry` (Protobuf field number 2; repeated=True)<br>`edge_tessellation: ansys.api.discovery.v1.design.geometry.body.GetTessellationResponseData.EdgeTessellationEntry` (Protobuf field number 3; repeated=True) |
| `GetVerticesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetVerticesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetVerticesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`vertices: ansys.api.discovery.v1.design.Vertex` (Protobuf field number 2; repeated=True) |
| `GetVolumeResponse` | `response_data: ansys.api.discovery.v1.design.geometry.body.GetVolumeResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetVolumeResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`volume: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `RemoveAssignedCADMaterialRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveAssignedCADMaterialResponse` | `successfully_removed_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `SetAssignedCADMaterialRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.SetAssignedCADMaterialRequestData` (Protobuf field number 1; repeated=True) |
| `SetAssignedCADMaterialRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`material: ansys.api.discovery.v1.design.MaterialEntity` (Protobuf field number 2; repeated=False) |
| `SetAssignedCADMaterialResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `SetFillStyleRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.SetFillStyleRequestData` (Protobuf field number 1; repeated=True) |
| `SetFillStyleRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`fill_style: ansys.api.discovery.v1.BodyFillStyle` (Protobuf field number 2; repeated=False) |
| `SetFillStyleResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceOffsetTypeRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.SetMidSurfaceOffsetTypeRequestData` (Protobuf field number 1; repeated=True) |
| `SetMidSurfaceOffsetTypeRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset_type: ansys.api.discovery.v1.MidSurfaceOffsetType` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceOffsetTypeResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceThicknessRequest` | `request_data: ansys.api.discovery.v1.design.geometry.body.SetMidSurfaceThicknessRequestData` (Protobuf field number 1; repeated=True) |
| `SetMidSurfaceThicknessRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`thickness: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceThicknessResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `SetSuppressedRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SetSuppressedResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.geometry.component_pb2`

| Message | Fields |
| --- | --- |
| `BeamBodies` | `beam_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ComponentBodies` | `component: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 2; repeated=True) |
| `CreateComponentData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`template_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False)<br>`instance_name: string` (Protobuf field number 4; repeated=False) |
| `CreateRequest` | `components: ansys.api.discovery.v1.design.geometry.components.CreateComponentData` (Protobuf field number 1; repeated=True) |
| `CreateResponse` | `components: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `components: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetBeamBodiesRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetBeamBodiesResponse` | `beam_bodies: ansys.api.discovery.v1.design.geometry.components.BeamBodies` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetBodiesResponse` | `bodies: ansys.api.discovery.v1.design.geometry.components.ComponentBodies` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetComponentNameResponse` | `names: ansys.api.discovery.v1.design.geometry.components.GetComponentNameResponse.NamesEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetPartResponse` | `parts: ansys.api.discovery.v1.design.geometry.components.GetPartResponse.PartsEntry` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `component: ansys.api.discovery.v1.design.ComponentEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetRootComponentRequest` | — |
| `GetRootComponentResponse` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ImportGroupsRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `ImportGroupsResponse` | `tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 1; repeated=False) |
| `MakeIndependentRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `MakeIndependentResponse` | `tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 1; repeated=False) |
| `MoveBodiesToComponentRequest` | `request_data: ansys.api.discovery.v1.design.geometry.components.MoveBodiesToComponentRequestData` (Protobuf field number 1; repeated=True) |
| `MoveBodiesToComponentRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`target_component_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `MoveBodiesToComponentResponse` | `tracked_changes: ansys.api.discovery.v1.design.TrackedChanges` (Protobuf field number 1; repeated=False) |
| `PlacementData` | `translation: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`rotation_axis_origin: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`rotation_axis_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False)<br>`rotation_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `SetPlacementRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`placements: ansys.api.discovery.v1.design.geometry.components.PlacementData` (Protobuf field number 2; repeated=True) |
| `SetPlacementResponse` | `matrices: ansys.api.discovery.v1.design.geometry.components.SetPlacementResponse.MatricesEntry` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `SetSharedTopologyRequest` | `shared_topologies: ansys.api.discovery.v1.design.geometry.components.SharedTopologyData` (Protobuf field number 1; repeated=True) |
| `SetSharedTopologyResponse` | `succesfully_applied: ansys.api.discovery.v1.design.geometry.components.SetSharedTopologyResponse.SuccesfullyAppliedEntry` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `SharedTopologyData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`share_type: ansys.api.discovery.v1.ShareType` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.geometry.curve_pb2`

| Message | Fields |
| --- | --- |
| `CreateCurvesFromProfileRequest` | `request_data: ansys.api.discovery.v1.design.geometry.curves.CreateCurvesFromProfileRequestData` (Protobuf field number 1; repeated=True) |
| `CreateCurvesFromProfileRequestData` | `geometries: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 3; repeated=False) |
| `CreateCurvesFromProfileResponse` | `created_curve_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateDesignPointsRequest` | `request_data: ansys.api.discovery.v1.design.geometry.curves.CreateDesignPointsRequestData` (Protobuf field number 1; repeated=True) |
| `CreateDesignPointsRequestData` | `points: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=True)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False) |
| `CreateDesignPointsResponse` | `created_point_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `EvaluateNurbsCurveRequest` | `curve: ansys.api.discovery.v1.design.NurbsCurve` (Protobuf field number 1; repeated=False)<br>`parameter: double` (Protobuf field number 2; repeated=False) |
| `EvaluateNurbsCurveResponse` | `curve_evaluation: ansys.api.discovery.v1.design.CurveEvaluation` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetIntervalResponse` | `response_data: ansys.api.discovery.v1.design.geometry.curves.GetIntervalResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetIntervalResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`start: double` (Protobuf field number 2; repeated=False)<br>`end: double` (Protobuf field number 3; repeated=False) |
| `GetResponse` | `curve: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetSuppressedRequest` | `curve_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SetSuppressedResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.geometry.edge_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetCurveResponse` | `response_data: ansys.api.discovery.v1.design.geometry.edges.GetCurveResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetCurveResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`curve: ansys.api.discovery.v1.design.CurveGeometry` (Protobuf field number 2; repeated=False) |
| `GetIntervalResponse` | `response_data: ansys.api.discovery.v1.design.geometry.edges.GetIntervalResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetIntervalResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`start: double` (Protobuf field number 2; repeated=False)<br>`end: double` (Protobuf field number 3; repeated=False) |
| `GetLengthResponse` | `response_data: ansys.api.discovery.v1.design.geometry.edges.GetLengthResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetLengthResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`length: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `edge: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetStartAndEndPointsResponse` | `response_data: ansys.api.discovery.v1.design.geometry.edges.GetStartAndEndPointsResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetStartAndEndPointsResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`start: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`end: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False) |
| `GetVerticesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.edges.GetVerticesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetVerticesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`vertices: ansys.api.discovery.v1.design.Vertex` (Protobuf field number 2; repeated=True) |

### `ansys.api.discovery.v1.design.geometry.face_pb2`

| Message | Fields |
| --- | --- |
| `CreateIsoParamCurvesRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.CreateIsoParamCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `CreateIsoParamCurvesRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`u_dir_curve: bool` (Protobuf field number 2; repeated=False)<br>`proportion: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `CreateIsoParamCurvesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.CreateIsoParamCurvesResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateIsoParamCurvesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 2; repeated=True) |
| `DetachFacesRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DetachFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `EvaluateRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.EvaluateRequestData` (Protobuf field number 1; repeated=True) |
| `EvaluateRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`u: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`v: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `EvaluateResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.EvaluateResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `EvaluateResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `FillFacesResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAreaResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetAreaResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetAreaResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`area: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetBoxUVResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetBoxUVResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetBoxUVResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`start_u: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`end_u: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`start_v: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`end_v: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `GetClosestSeparationRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.GetClosestSeparationRequestData` (Protobuf field number 1; repeated=True) |
| `GetClosestSeparationRequestData` | `face_1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`face_2_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `GetClosestSeparationResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetClosestSeparationResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetClosestSeparationResponseData` | `face_1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`face_2_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`separation: ansys.api.discovery.v1.design.Separation` (Protobuf field number 3; repeated=False) |
| `GetEdgesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetEdgesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetEdgesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True) |
| `GetExternalEdgesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetExternalEdgesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetExternalEdgesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True) |
| `GetFacesByAreaRangeRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`area1: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`area2: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `GetFacesByAreaRangeResponse` | `faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetInternalEdgesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetInternalEdgesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetInternalEdgesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True) |
| `GetLoopsResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetLoopsResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetLoopsResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`loops: ansys.api.discovery.v1.design.Loop` (Protobuf field number 2; repeated=True) |
| `GetNormalRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.GetNormalRequestData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetNormalRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`u: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`v: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `GetNormalResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetNormalResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetNormalResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `face: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetRoundInfoResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetRoundInfoResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetRoundInfoResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`along_u: bool` (Protobuf field number 2; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `GetSurfaceResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetSurfaceResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetSurfaceResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`surface: ansys.api.discovery.v1.design.Surface` (Protobuf field number 2; repeated=False) |
| `GetVerticesResponse` | `response_data: ansys.api.discovery.v1.design.geometry.face.GetVerticesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetVerticesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`vertices: ansys.api.discovery.v1.design.Vertex` (Protobuf field number 2; repeated=True) |
| `RemoveFacesRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.RemoveFacesRequestData` (Protobuf field number 1; repeated=True)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `RemoveFacesRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `RemoveFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ReplaceFaceRequest` | `target_selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`replacement_selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ReplaceFaceResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SetMidSurfaceOffsetTypeRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.SetMidSurfaceOffsetTypeRequestData` (Protobuf field number 1; repeated=True) |
| `SetMidSurfaceOffsetTypeRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset_type: ansys.api.discovery.v1.MidSurfaceOffsetType` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceOffsetTypeResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceThicknessRequest` | `request_data: ansys.api.discovery.v1.design.geometry.face.SetMidSurfaceThicknessRequestData` (Protobuf field number 1; repeated=True) |
| `SetMidSurfaceThicknessRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`thickness: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `SetMidSurfaceThicknessResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.geometry.mesh_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `meshes: ansys.api.discovery.v1.design.MeshEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `mesh: ansys.api.discovery.v1.design.MeshEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetSuppressedRequest` | `mesh_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |
| `SetSuppressedResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.geometry.part_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `parts: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetBeamsResponse` | `response_data: ansys.api.discovery.v1.design.geometry.part.GetBeamsResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetBeamsResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`beams: ansys.api.discovery.v1.design.BeamEntity` (Protobuf field number 2; repeated=True) |
| `GetResponse` | `part: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.parameters.drivingdimension_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `driving_dimensions: ansys.api.discovery.v1.design.DrivingDimensionEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `driving_dimension: ansys.api.discovery.v1.design.DrivingDimensionEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `SetDrivingDimensionRequest` | `request_data: ansys.api.discovery.v1.design.DrivingDimensionEntity` (Protobuf field number 1; repeated=True) |
| `SetDrivingDimensionResponse` | `response_data: ansys.api.discovery.v1.design.parameters.drivingdimension.SetDrivingDimensionResponseData` (Protobuf field number 1; repeated=True)<br>`set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 2; repeated=False) |
| `SetDrivingDimensionResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`status: ansys.api.discovery.v1.design.parameters.drivingdimension.UpdateStatus` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.parameters.historytrack_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `history_track_parameters: ansys.api.discovery.v1.design.parameters.historytrack.HistoryTrackParameterEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `history_track_parameter: ansys.api.discovery.v1.design.parameters.historytrack.HistoryTrackParameterEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `HistoryTrackParameterEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`dimension_type: ansys.api.discovery.v1.DimensionType` (Protobuf field number 3; repeated=False)<br>`dimension_value: double` (Protobuf field number 4; repeated=False) |
| `SetHistoryTrackRequest` | `request_data: ansys.api.discovery.v1.design.parameters.historytrack.HistoryTrackParameterEntity` (Protobuf field number 1; repeated=True) |
| `SetHistoryTrackResponse` | `response_data: ansys.api.discovery.v1.design.parameters.historytrack.HistoryTrackParameterEntity` (Protobuf field number 1; repeated=True)<br>`set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.parameters.script_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `script_parameters: ansys.api.discovery.v1.design.parameters.script.ScriptParameterEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `script_parameter: ansys.api.discovery.v1.design.parameters.script.ScriptParameterEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ScriptParameterEntity` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`dimension_type: ansys.api.discovery.v1.DimensionType` (Protobuf field number 3; repeated=False)<br>`dimension_value: double` (Protobuf field number 4; repeated=False) |
| `SetScriptParameterRequest` | `request_data: ansys.api.discovery.v1.design.parameters.script.ScriptParameterEntity` (Protobuf field number 1; repeated=True) |
| `SetScriptParameterResponse` | `response_data: ansys.api.discovery.v1.design.parameters.script.ScriptParameterEntity` (Protobuf field number 1; repeated=True)<br>`set_response: ansys.api.discovery.v1.SetResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.relationships.assemblycondition_pb2`

| Message | Fields |
| --- | --- |
| `CreateAlignRequest` | `request_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAlignRequestData` (Protobuf field number 1; repeated=True) |
| `CreateAlignRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometric_a_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`geometric_b_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateAlignResponse` | `response_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAlignResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateAlignResponseData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`align_condition: ansys.api.discovery.v1.design.AlignCondition` (Protobuf field number 2; repeated=False) |
| `CreateAnchorRequest` | `request_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAnchorRequestData` (Protobuf field number 1; repeated=True) |
| `CreateAnchorRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`component_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `CreateAnchorResponse` | `response_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateAnchorResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateAnchorResponseData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`anchor_condition: ansys.api.discovery.v1.design.AnchorCondition` (Protobuf field number 2; repeated=False) |
| `CreateGearRequest` | `request_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateGearRequestData` (Protobuf field number 1; repeated=True) |
| `CreateGearRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometric_a: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`geometric_b: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateGearResponse` | `response_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateGearResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateGearResponseData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`gear_condition: ansys.api.discovery.v1.design.GearCondition` (Protobuf field number 2; repeated=False) |
| `CreateOrientRequest` | `request_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateOrientRequestData` (Protobuf field number 1; repeated=True) |
| `CreateOrientRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometric_a_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`geometric_b_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateOrientResponse` | `response_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateOrientResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateOrientResponseData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`orient_condition: ansys.api.discovery.v1.design.OrientCondition` (Protobuf field number 2; repeated=False) |
| `CreateRigidRequest` | `request_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateRigidRequestData` (Protobuf field number 1; repeated=True) |
| `CreateRigidRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`component_a_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`component_b_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateRigidResponse` | `response_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateRigidResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateRigidResponseData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`rigid_condition: ansys.api.discovery.v1.design.RigidCondition` (Protobuf field number 2; repeated=False) |
| `CreateTangentRequest` | `request_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateTangentRequestData` (Protobuf field number 1; repeated=True) |
| `CreateTangentRequestData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`geometric_a_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`geometric_b_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateTangentResponse` | `response_data: ansys.api.discovery.v1.design.relationships.assemblycondition.CreateTangentResponseData` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `CreateTangentResponseData` | `parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`tangent_condition: ansys.api.discovery.v1.design.TangentCondition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.relationships.pattern_pb2`

| Message | Fields |
| --- | --- |
| `CircularPatternCreationRequest` | `request_data: ansys.api.discovery.v1.design.relationships.pattern.CircularPatternCreationRequestData` (Protobuf field number 1; repeated=True) |
| `CircularPatternCreationRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`circular_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`edge_axis_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False)<br>`line_axis: ansys.api.discovery.v1.Line` (Protobuf field number 4; repeated=False)<br>`circular_count: int32` (Protobuf field number 5; repeated=False)<br>`linear_count: int32` (Protobuf field number 6; repeated=False)<br>`linear_pitch: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`two_dimensional: bool` (Protobuf field number 8; repeated=False)<br>`radial_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 9; repeated=False) |
| `CircularPatternCreationResponse` | `tracked_creation_response: ansys.api.discovery.v1.design.TrackedCreationResponse` (Protobuf field number 1; repeated=False) |
| `FillPatternCreationRequest` | `request_data: ansys.api.discovery.v1.design.relationships.pattern.FillPatternCreationRequestData` (Protobuf field number 1; repeated=True) |
| `FillPatternCreationRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`column_x_offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`column_y_offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`fill_pattern_type: ansys.api.discovery.v1.FillPatternType` (Protobuf field number 4; repeated=False)<br>`linear_direction_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`margin: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`row_x_offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`row_y_offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 8; repeated=False)<br>`x_spacing: ansys.api.discovery.v1.Quantity` (Protobuf field number 9; repeated=False)<br>`y_spacing: ansys.api.discovery.v1.Quantity` (Protobuf field number 10; repeated=False) |
| `FillPatternCreationResponse` | `tracked_creation_response: ansys.api.discovery.v1.design.TrackedCreationResponse` (Protobuf field number 1; repeated=False) |
| `LinearPatternCreationRequest` | `request_data: ansys.api.discovery.v1.design.relationships.pattern.LinearPatternCreationRequestData` (Protobuf field number 1; repeated=True) |
| `LinearPatternCreationRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`two_dimensional: bool` (Protobuf field number 2; repeated=False)<br>`linear_direction_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False)<br>`count_x: int32` (Protobuf field number 4; repeated=False)<br>`count_y: int32` (Protobuf field number 5; repeated=False)<br>`pitch_x: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`pitch_y: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False) |
| `LinearPatternCreationResponse` | `tracked_creation_response: ansys.api.discovery.v1.design.TrackedCreationResponse` (Protobuf field number 1; repeated=False) |
| `RemoveMemberRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveMemberResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RemoveRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SetCircularPatternDataRequest` | `request_data: ansys.api.discovery.v1.design.relationships.pattern.SetCircularPatternDataRequestData` (Protobuf field number 1; repeated=True) |
| `SetCircularPatternDataRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`circular_count: int32` (Protobuf field number 2; repeated=False)<br>`linear_count: int32` (Protobuf field number 3; repeated=False)<br>`step_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`step_linear: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `SetCircularPatternDataResponse` | `tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 1; repeated=False) |
| `SetLinearPatternDataRequest` | `request_data: ansys.api.discovery.v1.design.relationships.pattern.SetLinearPatternDataRequestData` (Protobuf field number 1; repeated=True) |
| `SetLinearPatternDataRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`count_x: int32` (Protobuf field number 2; repeated=False)<br>`count_y: int32` (Protobuf field number 3; repeated=False)<br>`pitch_x: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`pitch_y: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`new_seed_index: int32` (Protobuf field number 6; repeated=False)<br>`old_seed_index: int32` (Protobuf field number 7; repeated=False) |
| `SetLinearPatternDataResponse` | `tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 1; repeated=False) |
| `SetPatternValueRequest` | `request_data: ansys.api.discovery.v1.design.relationships.pattern.SetPatternValueRequestData` (Protobuf field number 1; repeated=True) |
| `SetPatternValueRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`modification_type: ansys.api.discovery.v1.PatternModificationType` (Protobuf field number 2; repeated=False)<br>`value: double` (Protobuf field number 3; repeated=False) |
| `SetPatternValueResponse` | `tracked_set_response: ansys.api.discovery.v1.design.TrackedSetResponse` (Protobuf field number 1; repeated=False) |
| `UpdateFillRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `UpdateFillResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.design.selections.bodyselection_pb2`

| Message | Fields |
| --- | --- |
| `BodyGroup` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True) |
| `BodyGroupResponse` | `response_data: ansys.api.discovery.v1.design.selections.bodyselection.BodyGroupResponseData` (Protobuf field number 1; repeated=True) |
| `BodyGroupResponseData` | `groups: ansys.api.discovery.v1.design.selections.bodyselection.BodyGroup` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `BodySelectionExtendRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionExtendRequestData` (Protobuf field number 1; repeated=True) |
| `BodySelectionExtendRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`scope: ansys.api.discovery.v1.ExtendScope` (Protobuf field number 2; repeated=False) |
| `BodySelectionInputRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionInputRequestData` (Protobuf field number 1; repeated=True) |
| `BodySelectionInputRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `BodySelectionQueryResponse` | `response_data: ansys.api.discovery.v1.design.selections.bodyselection.BodySelectionQueryResponseData` (Protobuf field number 1; repeated=True) |
| `BodySelectionQueryResponseData` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ExtendNearbyBodiesRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.ExtendNearbyBodiesRequestData` (Protobuf field number 1; repeated=True) |
| `ExtendNearbyBodiesRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`scope: ansys.api.discovery.v1.ExtendScope` (Protobuf field number 3; repeated=False) |
| `FilterBodiesByColorRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByColorRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByColorRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`color: string` (Protobuf field number 2; repeated=False) |
| `FilterBodiesByCurveCountRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveCountRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByCurveCountRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False)<br>`min: int32` (Protobuf field number 3; repeated=False)<br>`max: int32` (Protobuf field number 4; repeated=False) |
| `FilterBodiesByCurveTypePercentileRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveTypePercentileRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByCurveTypePercentileRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False)<br>`min_percentile: double` (Protobuf field number 3; repeated=False)<br>`max_percentile: double` (Protobuf field number 4; repeated=False) |
| `FilterBodiesByCurveTypeRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByCurveTypeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByCurveTypeRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False) |
| `FilterBodiesByIntRangeRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByIntRangeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByIntRangeRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: int32` (Protobuf field number 2; repeated=False)<br>`max: int32` (Protobuf field number 3; repeated=False) |
| `FilterBodiesByNameRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByNameRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByNameRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`filter_type: ansys.api.discovery.v1.StringFilterType` (Protobuf field number 3; repeated=False)<br>`ignore_case: bool` (Protobuf field number 4; repeated=False) |
| `FilterBodiesBySurfaceAreaRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceAreaRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesBySurfaceAreaRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FilterBodiesBySurfaceCountRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceCountRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesBySurfaceCountRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`surface_type: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 2; repeated=False)<br>`min: int32` (Protobuf field number 3; repeated=False)<br>`max: int32` (Protobuf field number 4; repeated=False) |
| `FilterBodiesBySurfaceTypePercentileRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceTypePercentileRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesBySurfaceTypePercentileRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`surface_type: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 2; repeated=False)<br>`min_percentile: double` (Protobuf field number 3; repeated=False)<br>`max_percentile: double` (Protobuf field number 4; repeated=False) |
| `FilterBodiesBySurfaceTypeRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesBySurfaceTypeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesBySurfaceTypeRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`surface_type: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 2; repeated=False) |
| `FilterBodiesByVolumeRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesByVolumeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesByVolumeRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FilterBodiesContainingCurveTypesRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesContainingCurveTypesRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesContainingCurveTypesRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_types: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False)<br>`exclusive: bool` (Protobuf field number 3; repeated=False) |
| `FilterBodiesContainingSurfaceTypesRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesContainingSurfaceTypesRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesContainingSurfaceTypesRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`surface_types: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 2; repeated=False)<br>`exclusive: bool` (Protobuf field number 3; repeated=False) |
| `FilterBodiesPercentileRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.FilterBodiesPercentileRequestData` (Protobuf field number 1; repeated=True) |
| `FilterBodiesPercentileRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min_percentile: double` (Protobuf field number 2; repeated=False)<br>`max_percentile: double` (Protobuf field number 3; repeated=False) |
| `GetAllBodiesRequest` | — |
| `GetAllSolidBodiesRequest` | — |
| `GetAllSurfaceBodiesRequest` | — |
| `GetAllVisibleBodiesRequest` | — |
| `GetBodiesFromNamedSelectionRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesFromNamedSelectionRequestData` (Protobuf field number 1; repeated=True) |
| `GetBodiesFromNamedSelectionRequestData` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetBodiesWithColorRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithColorRequestData` (Protobuf field number 1; repeated=True) |
| `GetBodiesWithColorRequestData` | `color: string` (Protobuf field number 1; repeated=False) |
| `GetBodiesWithLocationRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithLocationRequestData` (Protobuf field number 1; repeated=True) |
| `GetBodiesWithLocationRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`range_type: ansys.api.discovery.v1.RangeType` (Protobuf field number 3; repeated=False) |
| `GetBodiesWithNameRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithNameRequestData` (Protobuf field number 1; repeated=True) |
| `GetBodiesWithNameRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`filter_type: ansys.api.discovery.v1.StringFilterType` (Protobuf field number 2; repeated=False)<br>`ignore_case: bool` (Protobuf field number 3; repeated=False) |
| `GetBodiesWithSurfaceAreaRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithSurfaceAreaRequestData` (Protobuf field number 1; repeated=True) |
| `GetBodiesWithSurfaceAreaRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetBodiesWithVolumeRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.GetBodiesWithVolumeRequestData` (Protobuf field number 1; repeated=True) |
| `GetBodiesWithVolumeRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `InvertBodySelectionRequest` | `request_data: ansys.api.discovery.v1.design.selections.bodyselection.InvertBodySelectionRequestData` (Protobuf field number 1; repeated=True) |
| `InvertBodySelectionRequestData` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`scope: ansys.api.discovery.v1.InvertScope` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.selections.edgeselection_pb2`

| Message | Fields |
| --- | --- |
| `EdgeGroup` | `edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 1; repeated=True) |
| `EdgeGroupResponse` | `response_data: ansys.api.discovery.v1.design.selections.edgeselection.EdgeGroupResponseData` (Protobuf field number 1; repeated=True) |
| `EdgeGroupResponseData` | `groups: ansys.api.discovery.v1.design.selections.edgeselection.EdgeGroup` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `EdgeSelectionExtendRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionExtendRequestData` (Protobuf field number 1; repeated=True) |
| `EdgeSelectionExtendRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`scope: ansys.api.discovery.v1.ExtendScope` (Protobuf field number 2; repeated=False)<br>`num_connected_edges: int32` (Protobuf field number 3; repeated=False) |
| `EdgeSelectionInputRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionInputRequestData` (Protobuf field number 1; repeated=True) |
| `EdgeSelectionInputRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `EdgeSelectionQueryResponse` | `response_data: ansys.api.discovery.v1.design.selections.edgeselection.EdgeSelectionQueryResponseData` (Protobuf field number 1; repeated=True) |
| `EdgeSelectionQueryResponseData` | `edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `ExtendNearbyEdgesRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.ExtendNearbyEdgesRequestData` (Protobuf field number 1; repeated=True) |
| `ExtendNearbyEdgesRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`scope: ansys.api.discovery.v1.ExtendScope` (Protobuf field number 3; repeated=False) |
| `FilterEdgesByCurveTypeRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.FilterEdgesByCurveTypeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterEdgesByCurveTypeRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False) |
| `FilterEdgesByLengthRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.FilterEdgesByLengthRequestData` (Protobuf field number 1; repeated=True) |
| `FilterEdgesByLengthRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FilterEdgesPercentileRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.FilterEdgesPercentileRequestData` (Protobuf field number 1; repeated=True) |
| `FilterEdgesPercentileRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min_percentile: double` (Protobuf field number 2; repeated=False)<br>`max_percentile: double` (Protobuf field number 3; repeated=False) |
| `GetAllEdgesRequest` | — |
| `GetAllVisibleEdgesRequest` | — |
| `GetEdgesFromNamedSelectionRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesFromNamedSelectionRequestData` (Protobuf field number 1; repeated=True) |
| `GetEdgesFromNamedSelectionRequestData` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetEdgesWithLengthRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesWithLengthRequestData` (Protobuf field number 1; repeated=True) |
| `GetEdgesWithLengthRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetEdgesWithLocationRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.GetEdgesWithLocationRequestData` (Protobuf field number 1; repeated=True) |
| `GetEdgesWithLocationRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`range_type: ansys.api.discovery.v1.RangeType` (Protobuf field number 3; repeated=False) |
| `InvertEdgeSelectionRequest` | `request_data: ansys.api.discovery.v1.design.selections.edgeselection.InvertEdgeSelectionRequestData` (Protobuf field number 1; repeated=True) |
| `InvertEdgeSelectionRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`scope: ansys.api.discovery.v1.InvertTopologyScope` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.selections.faceselection_pb2`

| Message | Fields |
| --- | --- |
| `FaceGroup` | `faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True) |
| `FaceGroupResponse` | `response_data: ansys.api.discovery.v1.design.selections.faceselection.FaceGroupResponseData` (Protobuf field number 1; repeated=True) |
| `FaceGroupResponseData` | `groups: ansys.api.discovery.v1.design.selections.faceselection.FaceGroup` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `FaceSelectionExtendRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionExtendRequestData` (Protobuf field number 1; repeated=True) |
| `FaceSelectionExtendRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`scope: ansys.api.discovery.v1.ExtendScope` (Protobuf field number 2; repeated=False) |
| `FaceSelectionInputRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionInputRequestData` (Protobuf field number 1; repeated=True) |
| `FaceSelectionInputRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FaceSelectionQueryResponse` | `response_data: ansys.api.discovery.v1.design.selections.faceselection.FaceSelectionQueryResponseData` (Protobuf field number 1; repeated=True) |
| `FaceSelectionQueryResponseData` | `faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `FilterFacesByAreaRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByAreaRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByAreaRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FilterFacesByColorRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByColorRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByColorRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`color: string` (Protobuf field number 2; repeated=False) |
| `FilterFacesByCurveCountRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveCountRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByCurveCountRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False)<br>`min: int32` (Protobuf field number 3; repeated=False)<br>`max: int32` (Protobuf field number 4; repeated=False) |
| `FilterFacesByCurveTypePercentileRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveTypePercentileRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByCurveTypePercentileRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False)<br>`min_percentile: double` (Protobuf field number 3; repeated=False)<br>`max_percentile: double` (Protobuf field number 4; repeated=False) |
| `FilterFacesByCurveTypeRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByCurveTypeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByCurveTypeRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False) |
| `FilterFacesByIntRangeRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByIntRangeRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByIntRangeRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: int32` (Protobuf field number 2; repeated=False)<br>`max: int32` (Protobuf field number 3; repeated=False) |
| `FilterFacesByPerimeterRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesByPerimeterRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesByPerimeterRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FilterFacesContainingCurveTypesRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesContainingCurveTypesRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesContainingCurveTypesRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_types: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False)<br>`exclusive: bool` (Protobuf field number 3; repeated=False) |
| `FilterFacesPercentileRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.FilterFacesPercentileRequestData` (Protobuf field number 1; repeated=True) |
| `FilterFacesPercentileRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`min_percentile: double` (Protobuf field number 2; repeated=False)<br>`max_percentile: double` (Protobuf field number 3; repeated=False) |
| `GetAllFacesRequest` | — |
| `GetAllVisibleFacesRequest` | — |
| `GetFacesFromNamedSelectionRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.GetFacesFromNamedSelectionRequestData` (Protobuf field number 1; repeated=True) |
| `GetFacesFromNamedSelectionRequestData` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetFacesWithAreaRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithAreaRequestData` (Protobuf field number 1; repeated=True) |
| `GetFacesWithAreaRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetFacesWithColorRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithColorRequestData` (Protobuf field number 1; repeated=True) |
| `GetFacesWithColorRequestData` | `color: string` (Protobuf field number 1; repeated=False) |
| `GetFacesWithLocationRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.GetFacesWithLocationRequestData` (Protobuf field number 1; repeated=True) |
| `GetFacesWithLocationRequestData` | `min: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`range_type: ansys.api.discovery.v1.RangeType` (Protobuf field number 3; repeated=False) |
| `InvertFaceSelectionRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.InvertFaceSelectionRequestData` (Protobuf field number 1; repeated=True) |
| `InvertFaceSelectionRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`scope: ansys.api.discovery.v1.InvertTopologyScope` (Protobuf field number 2; repeated=False) |
| `OrderFacesByCurveTypeRequest` | `request_data: ansys.api.discovery.v1.design.selections.faceselection.OrderFacesByCurveTypeRequestData` (Protobuf field number 1; repeated=True) |
| `OrderFacesByCurveTypeRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`curve_type: ansys.api.discovery.v1.CurveType` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.design.selections.namedselection_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `request_data: ansys.api.discovery.v1.design.selections.namedselection.CreateRequestData` (Protobuf field number 1; repeated=True) |
| `CreateRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`members_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `CreateResponse` | `named_selections: ansys.api.discovery.v1.design.NamedSelectionEntity` (Protobuf field number 1; repeated=True)<br>`creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 2; repeated=False) |
| `DeleteByNameRequest` | `name: string` (Protobuf field number 1; repeated=False) |
| `DeleteByNameResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `named_selections: ansys.api.discovery.v1.design.NamedSelectionEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `named_selection: ansys.api.discovery.v1.design.NamedSelectionEntity` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.engineeringdata.beamprofiledata_pb2`

| Message | Fields |
| --- | --- |
| `BeamDataDefinition` | `beam_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`source_library_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`data_object_name: string` (Protobuf field number 3; repeated=False)<br>`beam_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.BeamDataProperties` (Protobuf field number 4; repeated=False) |
| `BeamDataProperties` | — |
| `BeamDataResponse` | `library_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.BeamDataDefinition` (Protobuf field number 1; repeated=False) |
| `ChangeDataQuantityRequest` | `property_name: string` (Protobuf field number 1; repeated=False)<br>`quantity_data: ansys.api.discovery.v1.SetQuantityRequest` (Protobuf field number 2; repeated=False) |
| `CreateBeamProfileCircularRequest` | `request_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileCircularRequestData` (Protobuf field number 1; repeated=True) |
| `CreateBeamProfileCircularRequestData` | `plane: ansys.api.discovery.v1.Plane` (Protobuf field number 1; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`origin: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`name: string` (Protobuf field number 4; repeated=False) |
| `CreateBeamProfileCircularResponse` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `CreateBeamProfileSegmentsRequest` | `request_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileSegmentsRequestData` (Protobuf field number 1; repeated=True) |
| `CreateBeamProfileSegmentsRequestData` | `profile_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`lines: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=True)<br>`arcs: ansys.api.discovery.v1.Arc` (Protobuf field number 3; repeated=True)<br>`circles: ansys.api.discovery.v1.Circle` (Protobuf field number 4; repeated=True)<br>`planes: ansys.api.discovery.v1.Plane` (Protobuf field number 5; repeated=True)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 6; repeated=False) |
| `CreateBeamProfileSegmentsResponse` | `response_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateBeamProfileSegmentsResponseData` (Protobuf field number 1; repeated=True) |
| `CreateBeamProfileSegmentsResponseData` | `profile_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`beams_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `CreateDescriptiveProfileSegmentsResponse` | `response_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.CreateDescriptiveProfileSegmentsResponseData` (Protobuf field number 1; repeated=True) |
| `CreateDescriptiveProfileSegmentsResponseData` | `profile_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`beams: ansys.api.discovery.v1.design.BeamEntity` (Protobuf field number 2; repeated=True) |
| `DataLibraryRequest` | `data_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`source_library_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetBeamProfileCrossSectionInfoRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetBeamProfileCrossSectionInfoResponse` | `response_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfileCrossSectionInfoResponseData` (Protobuf field number 1; repeated=True) |
| `GetBeamProfileCrossSectionInfoResponseData` | `cross_section_info: ansys.api.discovery.v1.design.ProfileCrossSectionInfo` (Protobuf field number 1; repeated=False)<br>`id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetBeamProfileNameRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetBeamProfileNameResponse` | `name: string` (Protobuf field number 1; repeated=False) |
| `GetBeamProfilePartsRequest` | — |
| `GetBeamProfilePartsResponse` | `parts: ansys.api.discovery.v1.design.PartEntity` (Protobuf field number 1; repeated=True) |
| `GetBeamProfilePropertiesRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `GetBeamProfilePropertiesResponse` | `response_data: ansys.api.discovery.v1.engineeringdata.beamprofiledata.GetBeamProfilePropertiesResponseData` (Protobuf field number 1; repeated=True) |
| `GetBeamProfilePropertiesResponseData` | `properties: ansys.api.discovery.v1.design.ProfileProperties` (Protobuf field number 1; repeated=False)<br>`id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False) |
| `ImportLibraryDataRequest` | `json_library_data: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.engineeringdata.boltdata_pb2`

| Message | Fields |
| --- | --- |
| `BoltDataCreationResponse` | `condition_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.engineeringdata.boltdata.BoltDataDefinition` (Protobuf field number 2; repeated=False) |
| `BoltDataDefinition` | `id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`suppressed: bool` (Protobuf field number 4; repeated=False)<br>`bolt: ansys.api.discovery.v1.engineeringdata.boltdata.BoltDataProperties` (Protobuf field number 5; repeated=False) |
| `BoltDataLibraryRequest` | `label: string` (Protobuf field number 1; repeated=False) |
| `BoltDataProperties` | `material_name: string` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.engineeringdata.fandata_pb2`

| Message | Fields |
| --- | --- |
| `FanDataConvertToUserRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `FanDataCreationRequest` | `fan_data: ansys.api.discovery.v1.engineeringdata.fandata.FanDataProperties` (Protobuf field number 2; repeated=False) |
| `FanDataCreationResponse` | `data_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`engineering_data: ansys.api.discovery.v1.engineeringdata.fandata.FanDataDefinition` (Protobuf field number 2; repeated=False) |
| `FanDataDefinition` | `fan_data: ansys.api.discovery.v1.engineeringdata.fandata.FanDataProperties` (Protobuf field number 1; repeated=False) |
| `FanDataProperties` | `data_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`fan_name: string` (Protobuf field number 2; repeated=False)<br>`fan_specification: ansys.api.discovery.v1.engineeringdata.fandata.FanSpecification` (Protobuf field number 3; repeated=False)<br>`constant_pressure_rise: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`volume_flow_rate_vs_pressure_table: ansys.api.discovery.v1.QuantityPairTable` (Protobuf field number 5; repeated=False)<br>`velocity_vs_pressure_table: ansys.api.discovery.v1.QuantityPairTable` (Protobuf field number 6; repeated=False)<br>`manufacturer_data: ansys.api.discovery.v1.engineeringdata.fandata.FanManufacturerData` (Protobuf field number 7; repeated=False) |
| `FanManufacturerData` | `manufacturer: string` (Protobuf field number 1; repeated=False)<br>`model_number: string` (Protobuf field number 2; repeated=False)<br>`outer_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`inner_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`notes: string` (Protobuf field number 5; repeated=False)<br>`disclaimer: string` (Protobuf field number 6; repeated=False)<br>`is_user_defined: bool` (Protobuf field number 7; repeated=False) |
| `SetFanDataSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`fan_specification: ansys.api.discovery.v1.engineeringdata.fandata.FanSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.engineeringdata.material_pb2`

| Message | Fields |
| --- | --- |
| `MaterialCreationRequest` | `label: string` (Protobuf field number 1; repeated=False)<br>`material_state: ansys.api.discovery.v1.physics.MaterialState` (Protobuf field number 2; repeated=False)<br>`add_to_project: bool` (Protobuf field number 3; repeated=False)<br>`object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 4; repeated=False) |
| `MaterialCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`material_definition: ansys.api.discovery.v1.physics.MaterialDefinition` (Protobuf field number 2; repeated=False) |
| `MaterialDuplicateLibraryRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`new_label: string` (Protobuf field number 2; repeated=False) |
| `MaterialDuplicateLibraryResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`material_definition: ansys.api.discovery.v1.physics.MaterialDefinition` (Protobuf field number 2; repeated=False) |
| `MaterialGetByIdRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `MaterialGetByIdResponse` | `material_definition: ansys.api.discovery.v1.physics.MaterialDefinition` (Protobuf field number 1; repeated=False) |
| `MaterialGetByLabelRequest` | `label: string` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `MaterialGetByLabelResponse` | `material_definition: ansys.api.discovery.v1.physics.MaterialDefinition` (Protobuf field number 1; repeated=False) |
| `SetThermalConductivitySpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`thermal_conductivity_specification: ansys.api.discovery.v1.physics.ThermalConductivitySpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.engineeringdata.welddata_pb2`

| Message | Fields |
| --- | --- |
| `WeldDataCreationResponse` | `response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`engineering_data: ansys.api.discovery.v1.engineeringdata.welddata.WeldDataDefinition` (Protobuf field number 2; repeated=False) |
| `WeldDataDefinition` | `id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`suppressed: bool` (Protobuf field number 4; repeated=False)<br>`weld_properties: ansys.api.discovery.v1.engineeringdata.welddata.WeldDataProperties` (Protobuf field number 5; repeated=False) |
| `WeldDataLibraryRequest` | `label: string` (Protobuf field number 1; repeated=False) |
| `WeldDataProperties` | `type: ansys.api.discovery.v1.WeldType` (Protobuf field number 2; repeated=False)<br>`size: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`intermittent_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`minimum_pitch: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 5; repeated=False)<br>`max_number_along_length: ansys.api.discovery.v1.OptionalInt` (Protobuf field number 6; repeated=False) |

### `ansys.api.discovery.v1.operations.edit_pb2`

| Message | Fields |
| --- | --- |
| `BodiesSelectionResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True) |
| `BooleanRequest` | `body1_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`method: string` (Protobuf field number 3; repeated=False)<br>`tool_body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`keep_other: bool` (Protobuf field number 5; repeated=False) |
| `BooleanResponse` | `empty_result: int32` (Protobuf field number 1; repeated=False)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ChamferRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ChamferRequestData` (Protobuf field number 1; repeated=True) |
| `ChamferRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `ChamferResponse` | `response_data: ansys.api.discovery.v1.operations.edit.ChamferResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ChamferResponseData` | `success: bool` (Protobuf field number 1; repeated=False)<br>`created_faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 2; repeated=True)<br>`created_edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 3; repeated=True)<br>`created_surfaces: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 4; repeated=True)<br>`ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=False) |
| `CombineIntersectBodiesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.CombineIntersectBodiesRequestData` (Protobuf field number 1; repeated=True) |
| `CombineIntersectBodiesRequestData` | `target_selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tool_selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`keep_cutter: bool` (Protobuf field number 3; repeated=False)<br>`subtract_from_target: bool` (Protobuf field number 4; repeated=False)<br>`transfer_named_selections: bool` (Protobuf field number 5; repeated=False) |
| `CombineIntersectBodiesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `CombineMergeBodiesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.CombineMergeBodiesRequestData` (Protobuf field number 1; repeated=True) |
| `CombineMergeBodiesRequestData` | `target_selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `CombineMergeBodiesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `DetachFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.DetachFacesRequestData` (Protobuf field number 1; repeated=True) |
| `DetachFacesRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `DetachFacesResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `DraftFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.DraftFacesRequestData` (Protobuf field number 1; repeated=True) |
| `DraftFacesRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`reference_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`draft_side: ansys.api.discovery.v1.DraftSide` (Protobuf field number 3; repeated=False)<br>`draft_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 5; repeated=False) |
| `DraftFacesResponse` | `created_faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ExtrudeEdgesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ExtrudeEdgesRequestData` (Protobuf field number 1; repeated=True) |
| `ExtrudeEdgesRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`face_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 6; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 7; repeated=False)<br>`copy: bool` (Protobuf field number 8; repeated=False)<br>`natural_extension: bool` (Protobuf field number 9; repeated=False) |
| `ExtrudeEdgesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ExtrudeEdgesUpToRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ExtrudeEdgesUpToRequestData` (Protobuf field number 1; repeated=True) |
| `ExtrudeEdgesUpToRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`up_to_selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`seed_point: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 5; repeated=False) |
| `ExtrudeEdgesUpToResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ExtrudeFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ExtrudeFacesRequestData` (Protobuf field number 1; repeated=True) |
| `ExtrudeFacesRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 4; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 5; repeated=False)<br>`offset_mode: ansys.api.discovery.v1.OffsetMode` (Protobuf field number 6; repeated=False)<br>`copy: bool` (Protobuf field number 7; repeated=False)<br>`force_do_as_extrude: bool` (Protobuf field number 8; repeated=False) |
| `ExtrudeFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ExtrudeFacesUpToRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ExtrudeFacesUpToRequestData` (Protobuf field number 1; repeated=True) |
| `ExtrudeFacesUpToRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`up_to_selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 4; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 5; repeated=False)<br>`offset_mode: ansys.api.discovery.v1.OffsetMode` (Protobuf field number 6; repeated=False)<br>`copy: bool` (Protobuf field number 7; repeated=False)<br>`force_do_as_extrude: bool` (Protobuf field number 8; repeated=False)<br>`seed_point: ansys.api.discovery.v1.Point` (Protobuf field number 9; repeated=False) |
| `ExtrudeFacesUpToResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `FaceOffsetRequest` | `request_data: ansys.api.discovery.v1.operations.edit.FaceOffsetRequestData` (Protobuf field number 1; repeated=True) |
| `FaceOffsetRequestData` | `id1: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`id2: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`set_baselines: bool` (Protobuf field number 3; repeated=False)<br>`process_adjacent_faces: bool` (Protobuf field number 4; repeated=False) |
| `FaceOffsetResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `FillEdgeLoopsRequest` | `loops: ansys.api.discovery.v1.design.Loop` (Protobuf field number 1; repeated=True) |
| `FillEdgeLoopsResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `FillFacesRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FillFacesResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `FilletRequest` | `request_data: ansys.api.discovery.v1.operations.edit.FilletRequestData` (Protobuf field number 1; repeated=True) |
| `FilletRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FilletResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `FullFilletRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FullFilletResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ImprintCurvesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ImprintCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `ImprintCurvesRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`curves: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 2; repeated=False)<br>`face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=True)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 4; repeated=False)<br>`trimmed_curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 5; repeated=True) |
| `ImprintCurvesResponse` | `response_data: ansys.api.discovery.v1.operations.edit.ImprintCurvesResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ImprintCurvesResponseData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`created_entities: ansys.api.discovery.v1.design.EntitiesCollection` (Protobuf field number 2; repeated=False)<br>`deleted_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=True) |
| `ImprintProjectedCurvesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ImprintProjectedCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `ImprintProjectedCurvesRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`curves: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`closest_face: bool` (Protobuf field number 4; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 5; repeated=False) |
| `ImprintProjectedCurvesResponse` | `response_data: ansys.api.discovery.v1.operations.edit.ImprintProjectedCurvesResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ImprintProjectedCurvesResponseData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`created_entities: ansys.api.discovery.v1.design.EntitiesCollection` (Protobuf field number 2; repeated=False) |
| `IntersectCurveAndSurfaceRequest` | `request_data: ansys.api.discovery.v1.operations.edit.IntersectCurveAndSurfaceRequestData` (Protobuf field number 1; repeated=True) |
| `IntersectCurveAndSurfaceRequestData` | `curve: ansys.api.discovery.v1.design.CurveGeometry` (Protobuf field number 1; repeated=False)<br>`surface: ansys.api.discovery.v1.design.Surface` (Protobuf field number 2; repeated=False)<br>`surface_type: ansys.api.discovery.v1.SurfaceType` (Protobuf field number 3; repeated=False) |
| `IntersectCurveAndSurfaceResponse` | `response_data: ansys.api.discovery.v1.operations.edit.IntersectCurveAndSurfaceResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `IntersectCurveAndSurfaceResponseData` | `points: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=True)<br>`intersect: bool` (Protobuf field number 2; repeated=False) |
| `IntersectCurvesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.IntersectCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `IntersectCurvesRequestData` | `first: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 1; repeated=False)<br>`second: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 2; repeated=False) |
| `IntersectCurvesResponse` | `response_data: ansys.api.discovery.v1.operations.edit.IntersectCurvesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `IntersectCurvesResponseData` | `points: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=True)<br>`intersect: bool` (Protobuf field number 2; repeated=False) |
| `MapBodyRequest` | `request_data: ansys.api.discovery.v1.operations.edit.MapBodyRequestData` (Protobuf field number 1; repeated=True) |
| `MapBodyRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`frame: ansys.api.discovery.v1.Frame` (Protobuf field number 2; repeated=False) |
| `MapResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `MergeBodiesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.MergeBodiesRequestData` (Protobuf field number 1; repeated=True) |
| `MergeBodiesRequestData` | `target_selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`abort_on_error: bool` (Protobuf field number 2; repeated=False)<br>`can_make_independent: bool` (Protobuf field number 3; repeated=False)<br>`create_imprints: bool` (Protobuf field number 4; repeated=False) |
| `MergeBodiesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `MirrorRequest` | `request_data: ansys.api.discovery.v1.operations.edit.MirrorRequestData` (Protobuf field number 1; repeated=True) |
| `MirrorRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`mirror_plane: ansys.api.discovery.v1.Plane` (Protobuf field number 2; repeated=False)<br>`mirror_plane_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `MirrorResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `MoveImprintEdgesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.MoveImprintEdgesRequestData` (Protobuf field number 1; repeated=True) |
| `MoveImprintEdgesRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `MoveImprintEdgesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `MoveRotateRequest` | `request_data: ansys.api.discovery.v1.operations.edit.MoveRotateRequestData` (Protobuf field number 1; repeated=True) |
| `MoveRotateRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `MoveRotateResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `MoveTranslateRequest` | `request_data: ansys.api.discovery.v1.operations.edit.MoveTranslateRequestData` (Protobuf field number 1; repeated=True) |
| `MoveTranslateRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`named_selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=False) |
| `MoveTranslateResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `OffsetEdgesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.OffsetEdgesRequestData` (Protobuf field number 1; repeated=True) |
| `OffsetEdgesRequestData` | `edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`value: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `OffsetEdgesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `OffsetFaceCurvesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.OffsetFaceCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `OffsetFaceCurvesRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `OffsetFaceCurvesResponse` | `created_curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `OffsetFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.OffsetFacesRequestData` (Protobuf field number 1; repeated=True) |
| `OffsetFacesRequestData` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 4; repeated=False) |
| `OffsetFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `OffsetFacesSetRadiusRequest` | `request_data: ansys.api.discovery.v1.operations.edit.OffsetFacesSetRadiusRequestData` (Protobuf field number 1; repeated=True) |
| `OffsetFacesSetRadiusRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`copy: bool` (Protobuf field number 3; repeated=False)<br>`offset_mode: ansys.api.discovery.v1.OffsetMode` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 5; repeated=False)<br>`faces_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 6; repeated=True) |
| `OffsetFacesSetRadiusResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ProjectCurvesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ProjectCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `ProjectCurvesRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`curves: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`closest_face: bool` (Protobuf field number 4; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 5; repeated=False) |
| `ProjectCurvesResponse` | `response_data: ansys.api.discovery.v1.operations.edit.ProjectCurvesResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ProjectCurvesResponseData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 2; repeated=True) |
| `ProjectPointRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ProjectPointRequestData` (Protobuf field number 1; repeated=True) |
| `ProjectPointRequestData` | `curve: ansys.api.discovery.v1.design.NurbsCurve` (Protobuf field number 1; repeated=False)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `ProjectPointResponse` | `response_data: ansys.api.discovery.v1.operations.edit.ProjectPointResponseData` (Protobuf field number 1; repeated=True) |
| `ProjectPointResponseData` | `point: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`evaluation: ansys.api.discovery.v1.design.CurveEvaluation` (Protobuf field number 2; repeated=False) |
| `ProjectToSolidRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ProjectToSolidRequestData` (Protobuf field number 1; repeated=True) |
| `ProjectToSolidRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`target_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction_selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=False) |
| `ProjectToSolidResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `PullCurvePointRequest` | `request_data: ansys.api.discovery.v1.operations.edit.PullCurvePointRequestData` (Protobuf field number 1; repeated=True) |
| `PullCurvePointRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`linear: bool` (Protobuf field number 3; repeated=False)<br>`reversed: bool` (Protobuf field number 4; repeated=False) |
| `PullCurvePointResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RevolveCurvesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RevolveCurvesRequestData` (Protobuf field number 1; repeated=True) |
| `RevolveCurvesRequestData` | `curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`symmetric: bool` (Protobuf field number 4; repeated=False) |
| `RevolveCurvesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RevolveDatumPointByHelixRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RevolveDatumPointByHelixRequestData` (Protobuf field number 1; repeated=True) |
| `RevolveDatumPointByHelixRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=False)<br>`height: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`pitch: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`taper_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`right_handed: bool` (Protobuf field number 6; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 7; repeated=False) |
| `RevolveDatumPointByHelixResponse` | `response_data: ansys.api.discovery.v1.operations.edit.RevolveDatumPointByHelixResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `RevolveDatumPointByHelixResponseData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`created_curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 2; repeated=True) |
| `RevolveDatumPointRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RevolveDatumPointRequestData` (Protobuf field number 1; repeated=True) |
| `RevolveDatumPointRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `RevolveDatumPointResponse` | `response_data: ansys.api.discovery.v1.operations.edit.RevolveDatumPointResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `RevolveDatumPointResponseData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`created_curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 2; repeated=True) |
| `RevolveFacesByHelixRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RevolveFacesByHelixRequestData` (Protobuf field number 1; repeated=True) |
| `RevolveFacesByHelixRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 3; repeated=False)<br>`height: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`pitch: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`taper_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`right_handed: bool` (Protobuf field number 7; repeated=False)<br>`both_sides: bool` (Protobuf field number 8; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 9; repeated=False) |
| `RevolveFacesByHelixResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RevolveFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RevolveFacesRequestData` (Protobuf field number 1; repeated=True) |
| `RevolveFacesRequestData` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 2; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`alternate_axis_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`alternate_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 5; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 6; repeated=False) |
| `RevolveFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RevolveFacesUpToRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RevolveFacesUpToRequestData` (Protobuf field number 1; repeated=True) |
| `RevolveFacesUpToRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`up_to_selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`axis: ansys.api.discovery.v1.Line` (Protobuf field number 4; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 5; repeated=False) |
| `RevolveFacesUpToResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RotateOptions` | `angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`axis_origin: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`axis_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False) |
| `RotateRequest` | `request_data: ansys.api.discovery.v1.operations.edit.RotateRequestData` (Protobuf field number 1; repeated=True) |
| `RotateRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`options: ansys.api.discovery.v1.operations.edit.RotateOptions` (Protobuf field number 2; repeated=False) |
| `RotateResponse` | `successfully_set: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ScaleNonUniformRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ScaleNonUniformRequestData` (Protobuf field number 1; repeated=True) |
| `ScaleNonUniformRequestData` | `object_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`frame: ansys.api.discovery.v1.Frame` (Protobuf field number 2; repeated=False)<br>`scale_vector: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`keep_holes: bool` (Protobuf field number 4; repeated=False) |
| `ScaleNonUniformResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ScaleObjectRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ScaleObjectRequestData` (Protobuf field number 1; repeated=True) |
| `ScaleObjectRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`scale: double` (Protobuf field number 2; repeated=False) |
| `ScaleObjectResponse` | `successfully_set: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ScaleRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ScaleRequestData` (Protobuf field number 1; repeated=True) |
| `ScaleRequestData` | `object_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`point: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`optional_direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`scale: double` (Protobuf field number 4; repeated=False)<br>`keep_holes: bool` (Protobuf field number 5; repeated=False) |
| `ScaleResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `SeparatePiecesRequest` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `SeparatePiecesResponse` | `response_data: ansys.api.discovery.v1.operations.edit.SeparatePiecesResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `SeparatePiecesResponseData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`bodies: ansys.api.discovery.v1.operations.edit.BodiesSelectionResponse` (Protobuf field number 2; repeated=False) |
| `ShellRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ShellRequestData` (Protobuf field number 1; repeated=True) |
| `ShellRequestData` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `ShellResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SplitBodyRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SplitBodyRequestData` (Protobuf field number 1; repeated=True) |
| `SplitBodyRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`split_by_plane: ansys.api.discovery.v1.Plane` (Protobuf field number 2; repeated=False)<br>`split_by_slicer_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 3; repeated=True)<br>`split_by_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=True)<br>`extend_surfaces: bool` (Protobuf field number 5; repeated=False) |
| `SplitBodyResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SplitEdgesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SplitEdgesRequestData` (Protobuf field number 1; repeated=True) |
| `SplitEdgesRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`split_type: ansys.api.discovery.v1.operations.edit.SplitEdgeType` (Protobuf field number 2; repeated=False)<br>`proportions: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=True)<br>`points: ansys.api.discovery.v1.Point` (Protobuf field number 4; repeated=True)<br>`lengths: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=True)<br>`reference: ansys.api.discovery.v1.operations.edit.SplitEdgeReference` (Protobuf field number 6; repeated=False) |
| `SplitEdgesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SplitFaceRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SplitFaceRequestData` (Protobuf field number 1; repeated=True) |
| `SplitFaceRequestData` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`split_parameter: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False)<br>`split_start: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=False)<br>`split_end: ansys.api.discovery.v1.Point` (Protobuf field number 4; repeated=False)<br>`face_cutter_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 5; repeated=False)<br>`split_curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 6; repeated=True)<br>`split_type: ansys.api.discovery.v1.operations.edit.SplitFaceType` (Protobuf field number 7; repeated=False)<br>`parameter_type: ansys.api.discovery.v1.operations.edit.SplitFaceParameterType` (Protobuf field number 8; repeated=False) |
| `SplitFaceResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SweepDatumPointRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SweepDatumPointRequestData` (Protobuf field number 1; repeated=True) |
| `SweepDatumPointRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`trajectory_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`trajectory_curves: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 4; repeated=True) |
| `SweepDatumPointResponse` | `response_data: ansys.api.discovery.v1.operations.edit.SweepDatumPointResponseData` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `SweepDatumPointResponseData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`created_curves: ansys.api.discovery.v1.design.CurveEntity` (Protobuf field number 2; repeated=True) |
| `SweepEdgesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SweepEdgesRequestData` (Protobuf field number 1; repeated=True) |
| `SweepEdgesRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`trajectory_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`optional_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `SweepEdgesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SweepFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SweepFacesRequestData` (Protobuf field number 1; repeated=True) |
| `SweepFacesRequestData` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`trajectory_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`optional_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `SweepFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `SweepWithGuideRequest` | `request_data: ansys.api.discovery.v1.operations.edit.SweepWithGuideRequestData` (Protobuf field number 1; repeated=True) |
| `SweepWithGuideRequestData` | `name: string` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`plane: ansys.api.discovery.v1.Plane` (Protobuf field number 3; repeated=False)<br>`geometries: ansys.api.discovery.v1.design.Geometries` (Protobuf field number 4; repeated=False)<br>`path: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 5; repeated=False)<br>`guide: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 6; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 7; repeated=False) |
| `SweepWithGuideResponse` | `bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ThickenFacesRequest` | `request_data: ansys.api.discovery.v1.operations.edit.ThickenFacesRequestData` (Protobuf field number 1; repeated=True) |
| `ThickenFacesRequestData` | `ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`value: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`extrude_type: ansys.api.discovery.v1.ExtrudeType` (Protobuf field number 4; repeated=False)<br>`pull_symmetric: bool` (Protobuf field number 5; repeated=False)<br>`select_direction: bool` (Protobuf field number 6; repeated=False) |
| `ThickenFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `TranslateRequest` | `request_data: ansys.api.discovery.v1.operations.edit.TranslateRequestData` (Protobuf field number 1; repeated=True) |
| `TranslateRequestData` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`translation: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`distance: float` (Protobuf field number 3; repeated=False) |
| `TranslateResponse` | `successfully_set_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.operations.facet_pb2`

| Message | Fields |
| --- | --- |
| `FacetAutoFixRequest` | `selection: ansys.api.discovery.v1.design.MeshEntity` (Protobuf field number 1; repeated=True) |
| `FacetAutoFixResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapBodyRequest` | `selection: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.discovery.v1.operations.facet.ShrinkWrapOptions` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapBodyResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapMeshRequest` | `selection: ansys.api.discovery.v1.design.MeshEntity` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.discovery.v1.operations.facet.ShrinkWrapOptions` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapMeshResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ShrinkWrapOptions` | `size: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`keep_original_bodies: bool` (Protobuf field number 3; repeated=False)<br>`preserve_features: bool` (Protobuf field number 4; repeated=False)<br>`angle_tolerance: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`secondary_size_enabled: bool` (Protobuf field number 6; repeated=False)<br>`secondary_size: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`max_size_enabled: bool` (Protobuf field number 8; repeated=False)<br>`max_size: ansys.api.discovery.v1.Quantity` (Protobuf field number 9; repeated=False)<br>`curvature_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 10; repeated=False) |

### `ansys.api.discovery.v1.operations.measure_pb2`

| Message | Fields |
| --- | --- |
| `Gap` | `distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `MinDistanceBetweenObjectsRequest` | `bodies: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`selection: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `MinDistanceBetweenObjectsResponse` | `gap: ansys.api.discovery.v1.operations.measure.Gap` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `MinDistanceBetweenSelectionObjectsRequest` | `bodies: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`selection: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `MinDistanceBetweenSelectionObjectsResponse` | `gap: ansys.api.discovery.v1.operations.measure.Gap` (Protobuf field number 1; repeated=False)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.operations.prepare_pb2`

| Message | Fields |
| --- | --- |
| `CreateEnclosureBoxRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`x_low: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`x_high: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`y_low: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`y_high: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`z_low: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`z_high: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`enclosure_options: ansys.api.discovery.v1.operations.prepare.EnclosureOptions` (Protobuf field number 8; repeated=False) |
| `CreateEnclosureCylinderRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`axial_distance_low: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`axial_distance_high: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`radial_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`enclosure_options: ansys.api.discovery.v1.operations.prepare.EnclosureOptions` (Protobuf field number 5; repeated=False) |
| `CreateEnclosureResponse` | `created_bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `CreateEnclosureSphereRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`radial_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`enclosure_options: ansys.api.discovery.v1.operations.prepare.EnclosureOptions` (Protobuf field number 3; repeated=False) |
| `DetectSweepableBodiesRequest` | `bodies: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`get_source_target_faces: bool` (Protobuf field number 2; repeated=False) |
| `DetectSweepableBodiesResponse` | `response_data: ansys.api.discovery.v1.operations.prepare.DetectSweepableBodiesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `DetectSweepableBodiesResponseData` | `result: bool` (Protobuf field number 1; repeated=False)<br>`face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `EnclosureOptions` | `create_shared_topology: bool` (Protobuf field number 1; repeated=False)<br>`subtract_bodies: bool` (Protobuf field number 2; repeated=False)<br>`frame: ansys.api.discovery.v1.Frame` (Protobuf field number 3; repeated=False)<br>`cushion_proportion: double` (Protobuf field number 4; repeated=False) |
| `EnhancedShareTopologyResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False)<br>`found: int32` (Protobuf field number 2; repeated=False)<br>`repaired: int32` (Protobuf field number 3; repeated=False) |
| `ExtractVolumeFromEdgeLoopsRequest` | `sealing_edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`inside_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ExtractVolumeFromEdgeLoopsResponse` | `created_bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `ExtractVolumeFromFacesRequest` | `sealing_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`inside_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ExtractVolumeFromFacesResponse` | `created_bodies: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `FindAndRemoveLogosRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.discovery.v1.operations.prepare.FindLogoOptions` (Protobuf field number 2; repeated=False) |
| `FindAndRemoveLogosResponse` | `logo_faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 2; repeated=False) |
| `FindHelixesOptions` | `min_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`max_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`fit_radius_error: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FindHelixesRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.discovery.v1.operations.prepare.FindHelixesOptions` (Protobuf field number 2; repeated=False) |
| `FindHelixesResponse` | `helixes: ansys.api.discovery.v1.operations.prepare.FindHelixesResponseData` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `FindHelixesResponseData` | `trimmed_curve: ansys.api.discovery.v1.design.TrimmedCurve` (Protobuf field number 1; repeated=False)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 2; repeated=True) |
| `FindLogoOptions` | `min_height: double` (Protobuf field number 1; repeated=False)<br>`max_height: double` (Protobuf field number 2; repeated=False)<br>`max_fillet_radio_as_sharp: double` (Protobuf field number 3; repeated=False)<br>`fit_error: double` (Protobuf field number 4; repeated=False) |
| `FindLogosRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.discovery.v1.operations.prepare.FindLogoOptions` (Protobuf field number 2; repeated=False) |
| `FindLogosResponse` | `logo_faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 1; repeated=True)<br>`command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 2; repeated=False) |
| `FindMappableFacesRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FindMappableFacesResponse` | `response_data: ansys.api.discovery.v1.operations.prepare.FindMappableFacesResponseData` (Protobuf field number 1; repeated=True) |
| `FindMappableFacesResponseData` | `face: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`mappable: bool` (Protobuf field number 2; repeated=False) |
| `FixInterferenceRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`cut_smaller_body: bool` (Protobuf field number 2; repeated=False) |
| `FixInterferenceResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `FixShortEdgesRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`max_edge_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FixShortEdgesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RemoveFacesRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveFacesResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RemoveLogoRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RemoveLogoResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `RemoveRoundsRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`auto_shrink: bool` (Protobuf field number 2; repeated=False) |
| `RemoveRoundsResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `ShareTopologyRequest` | `selection_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tolerance: double` (Protobuf field number 2; repeated=False)<br>`preserve_instances: bool` (Protobuf field number 3; repeated=False) |
| `ShareTopologyResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |
| `UnshareTopologyRequest` | `include_groups: bool` (Protobuf field number 1; repeated=False)<br>`unshare_lower_topology: bool` (Protobuf field number 2; repeated=False) |
| `UnshareTopologyResponse` | `tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.operations.rayfire_pb2`

| Message | Fields |
| --- | --- |
| `FireAdditionalOptions` | `radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False)<br>`max_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`min_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 5; repeated=False)<br>`pick_back_faces: bool` (Protobuf field number 6; repeated=False)<br>`max_hits: int32` (Protobuf field number 7; repeated=False)<br>`request_params: bool` (Protobuf field number 8; repeated=False)<br>`request_secondary: bool` (Protobuf field number 9; repeated=False) |
| `FireFacesRequest` | `request_data: ansys.api.discovery.v1.operations.rayfire.FireFacesRequestData` (Protobuf field number 1; repeated=True) |
| `FireFacesRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`points: ansys.api.discovery.v1.Point` (Protobuf field number 3; repeated=True)<br>`options: ansys.api.discovery.v1.operations.rayfire.FireAdditionalOptions` (Protobuf field number 4; repeated=False) |
| `FireFacesResponse` | `response_data: ansys.api.discovery.v1.operations.rayfire.FireFacesResponseData` (Protobuf field number 1; repeated=True) |
| `FireFacesResponseData` | `faces_fire_impacts: ansys.api.discovery.v1.RayFireFaceImpacts` (Protobuf field number 1; repeated=True) |
| `FireOrderedRequest` | `request_data: ansys.api.discovery.v1.operations.rayfire.FireOrderedRequestData` (Protobuf field number 1; repeated=True) |
| `FireOrderedRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`ray_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`points: ansys.api.discovery.v1.Point` (Protobuf field number 5; repeated=True)<br>`max_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 7; repeated=False) |
| `FireOrderedResponse` | `response_data: ansys.api.discovery.v1.operations.rayfire.FireOrderedResponseData` (Protobuf field number 1; repeated=True) |
| `FireOrderedResponseData` | `ordered_fire_impacts: ansys.api.discovery.v1.RayFireImpacts` (Protobuf field number 1; repeated=True) |
| `FireOrderedUVRequest` | `request_data: ansys.api.discovery.v1.operations.rayfire.FireOrderedUVRequestData` (Protobuf field number 1; repeated=True) |
| `FireOrderedUVRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`ray_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`points: ansys.api.discovery.v1.Point` (Protobuf field number 5; repeated=True)<br>`max_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`tight_tolerance: bool` (Protobuf field number 7; repeated=False) |
| `FireOrderedUVResponse` | `response_data: ansys.api.discovery.v1.operations.rayfire.FireOrderedUVResponseData` (Protobuf field number 1; repeated=True) |
| `FireOrderedUVResponseData` | `ordered_fire_impacts: ansys.api.discovery.v1.RayFireUVImpacts` (Protobuf field number 1; repeated=True) |
| `FireRequest` | `request_data: ansys.api.discovery.v1.operations.rayfire.FireRequestData` (Protobuf field number 1; repeated=True) |
| `FireRequestData` | `body_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`faces_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 3; repeated=False)<br>`points: ansys.api.discovery.v1.Point` (Protobuf field number 4; repeated=True)<br>`max_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `FireResponse` | `response_data: ansys.api.discovery.v1.operations.rayfire.FireResponseData` (Protobuf field number 1; repeated=True) |
| `FireResponseData` | `single_ray_fire_impacts: ansys.api.discovery.v1.RayFireImpacts` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.operations.repair_pb2`

| Message | Fields |
| --- | --- |
| `AdjustMergeFacesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tangent_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`allow_multi_patch: bool` (Protobuf field number 3; repeated=False)<br>`fail_if_can_fill: bool` (Protobuf field number 4; repeated=False)<br>`enforce_closed_loop_check: bool` (Protobuf field number 5; repeated=False) |
| `AdjustMergeFacesResponse` | `result: bool` (Protobuf field number 1; repeated=False) |
| `AdjustSimplifyProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `CurveGapProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`curve_point_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `DuplicateCurveProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`curve_point_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `DuplicateFaceProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ExtraEdgeProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `FindAdjustMergeFacesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`tangent_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True)<br>`allow_multi_patch: bool` (Protobuf field number 3; repeated=False)<br>`fail_if_can_fill: bool` (Protobuf field number 4; repeated=False)<br>`enforce_closed_loop_check: bool` (Protobuf field number 5; repeated=False) |
| `FindAdjustMergeFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.SplitEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindAdjustSimplifyRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`comprehensive: bool` (Protobuf field number 2; repeated=False) |
| `FindAdjustSimplifyResponse` | `result: ansys.api.discovery.v1.operations.repair.AdjustSimplifyProblemArea` (Protobuf field number 1; repeated=True) |
| `FindAndFixExtraEdgesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`comprehensive: bool` (Protobuf field number 2; repeated=False) |
| `FindAndFixExtraEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FindAndFixShortEdgesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`max_edge_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`comprehensive: bool` (Protobuf field number 3; repeated=False) |
| `FindAndFixShortEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FindAndFixSplitEdgesRequest` | `bodys_or_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`comprehensive: bool` (Protobuf field number 4; repeated=False) |
| `FindAndFixSplitEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FindAndFixStitchFacesRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`maximum_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`check_for_coincidence: bool` (Protobuf field number 3; repeated=False)<br>`allow_multiple_bodies: bool` (Protobuf field number 4; repeated=False)<br>`maintain_components: bool` (Protobuf field number 5; repeated=False)<br>`comprehensive: bool` (Protobuf field number 6; repeated=False) |
| `FindAndFixStitchFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FindAndSimplifyRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`comprehensive: bool` (Protobuf field number 2; repeated=False) |
| `FindAndSimplifyResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FindBadFacesRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FindBadFacesResponse` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FindCurveGapsRequest` | `distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `FindCurveGapsResponse` | `result: ansys.api.discovery.v1.operations.repair.CurveGapProblemArea` (Protobuf field number 1; repeated=True) |
| `FindDuplicateCurvesRequest` | — |
| `FindDuplicateCurvesResponse` | `result: ansys.api.discovery.v1.operations.repair.DuplicateCurveProblemArea` (Protobuf field number 1; repeated=True) |
| `FindDuplicateFacesRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`max_gap: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FindDuplicateFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.DuplicateFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindExtraEdgesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`comprehensive: bool` (Protobuf field number 2; repeated=False) |
| `FindExtraEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.ExtraEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindGapsRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`fix_method: ansys.api.discovery.v1.operations.repair.SolidifyFixMethodType` (Protobuf field number 4; repeated=False)<br>`allow_multi_patch: bool` (Protobuf field number 5; repeated=False) |
| `FindGapsResponse` | `result: ansys.api.discovery.v1.operations.repair.GapProblemArea` (Protobuf field number 1; repeated=True) |
| `FindInexactEdgesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `FindInexactEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.InexactEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindInterferenceRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`cut_smaller_body: bool` (Protobuf field number 2; repeated=False) |
| `FindInterferenceResponse` | `result: ansys.api.discovery.v1.operations.repair.FixInterferenceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindMissingFacesRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`null: google.protobuf.NullValue` (Protobuf field number 4; repeated=False)<br>`data: ansys.api.discovery.v1.operations.repair.SolidifyFixMethodType` (Protobuf field number 5; repeated=False)<br>`allow_multi_patch: bool` (Protobuf field number 6; repeated=False) |
| `FindMissingFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.MissingFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindShortEdgesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`max_edge_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`comprehensive: bool` (Protobuf field number 3; repeated=False) |
| `FindShortEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.ShortEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindSmallCurvesRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`max_curve_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FindSmallCurvesResponse` | `result: ansys.api.discovery.v1.operations.repair.SmallCurveProblemArea` (Protobuf field number 1; repeated=True) |
| `FindSmallFacesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`area: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`width: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `FindSmallFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.SmallFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FindSplitEdgesRequest` | `body_or_face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`comprehensive: bool` (Protobuf field number 4; repeated=False) |
| `FindSplitEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.SplitEdgeProblemArea` (Protobuf field number 1; repeated=True) |
| `FindStitchFacesRequest` | `face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`maximum_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`check_for_coincidence: bool` (Protobuf field number 3; repeated=False)<br>`allow_multiple_bodies: bool` (Protobuf field number 4; repeated=False)<br>`maintain_components: bool` (Protobuf field number 5; repeated=False)<br>`comprehensive: bool` (Protobuf field number 6; repeated=False) |
| `FindStitchFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.StitchFaceProblemArea` (Protobuf field number 1; repeated=True) |
| `FitCurvesRequest` | `selection_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`arcs: bool` (Protobuf field number 2; repeated=False)<br>`lines: bool` (Protobuf field number 3; repeated=False)<br>`splines: bool` (Protobuf field number 4; repeated=False)<br>`tangentize: bool` (Protobuf field number 5; repeated=False)<br>`tolerance: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `FitCurvesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixAdjustSimplifyRequest` | `adjust_simplify_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixAdjustSimplifyResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixCurveGapsRequest` | `curve_gap_problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FixCurveGapsResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixDuplicateCurvesRequest` | `duplicate_curve_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixDuplicateCurvesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixDuplicateFacesRequest` | `duplicate_face_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixDuplicateFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixExtraEdgesRequest` | `extra_edge_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixExtraEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixGapsRequest` | `gap_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixGapsResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixInexactEdgesRequest` | `inexact_edge_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixInexactEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixInterferenceProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `FixInterferenceRequest` | `interference_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixInterferenceResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixMissingFacesRequest` | `missing_face_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixMissingFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixShortEdgesRequest` | `short_edge_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixShortEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixSmallCurvesRequest` | `small_curve_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixSmallCurvesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixSmallFacesRequest` | `small_face_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixSmallFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixSplitEdgeOptions` | `max_edge_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`min_edge_angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FixSplitEdgesRequest` | `split_edge_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixSplitEdgesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `FixStitchFacesRequest` | `stitch_face_problem_area_id: int32` (Protobuf field number 1; repeated=False) |
| `FixStitchFacesResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `GapProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `GenericProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `InexactEdgeProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `InspectGeometryOptions` | `level: ansys.api.discovery.v1.InspectGeometryLevel` (Protobuf field number 1; repeated=False)<br>`max_number_of_issues: int32` (Protobuf field number 2; repeated=False)<br>`check_self_intersections: bool` (Protobuf field number 3; repeated=False)<br>`find_g1_discontinuities: bool` (Protobuf field number 4; repeated=False)<br>`sliver_edge_tolerance: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`sliver_face_tolerance: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `InspectGeometryRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`options: ansys.api.discovery.v1.operations.repair.InspectGeometryOptions` (Protobuf field number 2; repeated=False) |
| `InspectGeometryResponse` | `issues_by_body: ansys.api.discovery.v1.operations.repair.InspectGeometryResult` (Protobuf field number 1; repeated=True) |
| `InspectGeometryResult` | `body: ansys.api.discovery.v1.design.BodyEntity` (Protobuf field number 1; repeated=False)<br>`issues: ansys.api.discovery.v1.operations.repair.InspectGeometryResultIssue` (Protobuf field number 2; repeated=True) |
| `InspectGeometryResultIssue` | `message_type: ansys.api.discovery.v1.InspectGeometryMessageType` (Protobuf field number 1; repeated=False)<br>`message_id: ansys.api.discovery.v1.InspectGeometryMessageId` (Protobuf field number 2; repeated=False)<br>`faces: ansys.api.discovery.v1.design.FaceEntity` (Protobuf field number 3; repeated=True)<br>`edges: ansys.api.discovery.v1.design.EdgeEntity` (Protobuf field number 4; repeated=True)<br>`message: string` (Protobuf field number 5; repeated=False)<br>`scalar_value: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `MissingFaceProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `RepairGeometryRequest` | `body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True) |
| `RepairGeometryResponse` | `result: ansys.api.discovery.v1.operations.repair.RepairToolMessage` (Protobuf field number 1; repeated=False) |
| `RepairToolMessage` | `found: int32` (Protobuf field number 1; repeated=False)<br>`repaired: int32` (Protobuf field number 2; repeated=False)<br>`tracked_command_response: ansys.api.discovery.v1.design.TrackedCommandResponse` (Protobuf field number 3; repeated=False) |
| `ShortEdgeProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `SmallCurveProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`curve_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `SmallFaceProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`face_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `SplitEdgeProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`edge_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `StitchFaceProblemArea` | `problem_area_id: int32` (Protobuf field number 1; repeated=False)<br>`body_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |

### `ansys.api.discovery.v1.operations.sketch_pb2`

| Message | Fields |
| --- | --- |
| `CreateSketchLineRequest` | `request_data: ansys.api.discovery.v1.operations.sketch.CreateSketchLineRequestData` (Protobuf field number 1; repeated=True) |
| `CreateSketchLineRequestData` | `point1: ansys.api.discovery.v1.Point` (Protobuf field number 1; repeated=False)<br>`point2: ansys.api.discovery.v1.Point` (Protobuf field number 2; repeated=False) |
| `CreateSketchLineResponse` | `successfully_set: int32` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.assignments.beamassignment_pb2`

| Message | Fields |
| --- | --- |
| `BeamAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`beam_data: ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentProperties` (Protobuf field number 2; repeated=False) |
| `BeamAssignmentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `BeamAssignmentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`beam_data: ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `BeamAssignmentProperties` | `beam_definition: ansys.api.discovery.v1.engineeringdata.beamprofiledata.BeamDataDefinition` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.assignments.beamassignment.BeamAssignmentDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.assignments.boltassignment_pb2`

| Message | Fields |
| --- | --- |
| `BoltAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`bolt_assignment_properties: ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentProperties` (Protobuf field number 2; repeated=False)<br>`create_long_bolts: bool` (Protobuf field number 3; repeated=False) |
| `BoltAssignmentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `BoltAssignmentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`bolt: ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `BoltAssignmentProperties` | `definition: ansys.api.discovery.v1.engineeringdata.boltdata.BoltDataDefinition` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.assignments.boltassignment.BoltAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `SetBoltLocationRequest` | `set_location_request: ansys.api.discovery.v1.SetLocationRequest` (Protobuf field number 1; repeated=False)<br>`create_long_bolts: bool` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.physics.assignments.fanassignment_pb2`

| Message | Fields |
| --- | --- |
| `ExternalFanAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`fan_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`external_fan_assignment_properties: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `ExternalFanAssignmentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `ExternalFanAssignmentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`assignment_properties: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `ExternalFanAssignmentProperties` | `fan_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanSpecification` (Protobuf field number 2; repeated=False)<br>`gauge_pressure: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`is_swirling: bool` (Protobuf field number 4; repeated=False)<br>`flow_temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `GetAllExternalResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentDefinition` (Protobuf field number 2; repeated=True) |
| `GetAllInternalResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentDefinition` (Protobuf field number 2; repeated=True) |
| `GetExternalSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `GetInternalSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `InternalFanAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`fan_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`internal_fan_assignment_properties: ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `InternalFanAssignmentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `InternalFanAssignmentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`assignment_properties: ansys.api.discovery.v1.physics.assignments.fanassignment.InternalFanAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `InternalFanAssignmentProperties` | `fan_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`is_shrouded: bool` (Protobuf field number 2; repeated=False)<br>`total_heat: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 3; repeated=False)<br>`hub_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`tip_radius: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`is_swirling: bool` (Protobuf field number 6; repeated=False)<br>`inlet_face_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=False) |
| `SetExternalFanSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.assignments.fanassignment.ExternalFanSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.assignments.filletweldassignment_pb2`

| Message | Fields |
| --- | --- |
| `FilletWeldAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`fillet_weld_assignment_properties: ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentProperties` (Protobuf field number 2; repeated=False) |
| `FilletWeldAssignmentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `FilletWeldAssignmentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`fillet_weld: ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentProperties` (Protobuf field number 3; repeated=False)<br>`generated_pitch: double` (Protobuf field number 4; repeated=False)<br>`number_of_intermittent_welds: int32` (Protobuf field number 5; repeated=False) |
| `FilletWeldAssignmentProperties` | `definition: ansys.api.discovery.v1.engineeringdata.welddata.WeldDataDefinition` (Protobuf field number 1; repeated=False)<br>`min_detection_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`max_detection_distance: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.assignments.filletweldassignment.FilletWeldAssignmentDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.assignments.materialassignment_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentDefinition` (Protobuf field number 2; repeated=False) |
| `MaterialAssignmentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`material_assignment_properties: ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentProperties` (Protobuf field number 2; repeated=False)<br>`enable_compressible_flow: bool` (Protobuf field number 3; repeated=False)<br>`enable_thermal_effects: bool` (Protobuf field number 4; repeated=False) |
| `MaterialAssignmentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`new_assignment_created: bool` (Protobuf field number 2; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentDefinition` (Protobuf field number 3; repeated=False) |
| `MaterialAssignmentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`assignment_properties: ansys.api.discovery.v1.physics.assignments.materialassignment.MaterialAssignmentProperties` (Protobuf field number 3; repeated=False) |
| `MaterialAssignmentProperties` | `material_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`assembled_temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.acceleration_pb2`

| Message | Fields |
| --- | --- |
| `AccelerationCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`acceleration_properties: ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationProperties` (Protobuf field number 2; repeated=False) |
| `AccelerationCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationDefinition` (Protobuf field number 2; repeated=False) |
| `AccelerationDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`acceleration: ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationProperties` (Protobuf field number 3; repeated=False) |
| `AccelerationProperties` | `acceleration: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.acceleration.AccelerationDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.bearing_pb2`

| Message | Fields |
| --- | --- |
| `BearingCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`bearing_properties: ansys.api.discovery.v1.physics.conditions.bearing.BearingProperties` (Protobuf field number 2; repeated=False) |
| `BearingCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.bearing.BearingDefinition` (Protobuf field number 2; repeated=False) |
| `BearingDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`bearing: ansys.api.discovery.v1.physics.conditions.bearing.BearingProperties` (Protobuf field number 3; repeated=False) |
| `BearingProperties` | `radial_force: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`thrust_force: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`angle: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.bearing.BearingDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.bearing.BearingDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.boltpreload_pb2`

| Message | Fields |
| --- | --- |
| `BoltPreloadClampForceCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`clamp_force_properties: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadClampForceProperties` (Protobuf field number 2; repeated=False) |
| `BoltPreloadClampForceProperties` | `clamp_force: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `BoltPreloadCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadDefinition` (Protobuf field number 2; repeated=False) |
| `BoltPreloadDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`side1_locations: string` (Protobuf field number 2; repeated=True)<br>`side2_locations: string` (Protobuf field number 3; repeated=True)<br>`specification: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadSpecification` (Protobuf field number 4; repeated=False)<br>`clamp_force_properties: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadClampForceProperties` (Protobuf field number 5; repeated=False)<br>`grip_length_properties: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadGripLengthProperties` (Protobuf field number 6; repeated=False)<br>`torque_properties: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadTorqueProperties` (Protobuf field number 7; repeated=False) |
| `BoltPreloadGripLengthCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`grip_length_properties: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadGripLengthProperties` (Protobuf field number 2; repeated=False) |
| `BoltPreloadGripLengthProperties` | `grip_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `BoltPreloadTorqueCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`torque_properties: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadTorqueProperties` (Protobuf field number 2; repeated=False) |
| `BoltPreloadTorqueProperties` | `torque: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`torque_coefficient: double` (Protobuf field number 2; repeated=False)<br>`boltdiameter: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 3; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadDefinition` (Protobuf field number 2; repeated=False) |
| `SetBoltPreloadSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.conditions.boltpreload.BoltPreloadSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.convection_pb2`

| Message | Fields |
| --- | --- |
| `ConvectionCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`coefficient: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `ConvectionCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.convection.ConvectionDefinition` (Protobuf field number 2; repeated=False) |
| `ConvectionDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`coefficient: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.convection.ConvectionDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.convection.ConvectionDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.current_pb2`

| Message | Fields |
| --- | --- |
| `CurrentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`current_properties: ansys.api.discovery.v1.physics.conditions.current.CurrentProperties` (Protobuf field number 2; repeated=False) |
| `CurrentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.current.CurrentDefinition` (Protobuf field number 2; repeated=False) |
| `CurrentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`current: ansys.api.discovery.v1.physics.conditions.current.CurrentProperties` (Protobuf field number 3; repeated=False) |
| `CurrentProperties` | `current_magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.current.CurrentDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.current.CurrentDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.displacement_pb2`

| Message | Fields |
| --- | --- |
| `ChangeDisplacementSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`displacement_specification: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementSpecification` (Protobuf field number 2; repeated=False) |
| `DisplacementCombinedCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`displacement_properties: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementCombinedProperties` (Protobuf field number 2; repeated=False) |
| `DisplacementCombinedProperties` | `displacement: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`rotation: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 2; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 3; repeated=False) |
| `DisplacementCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementDefinition` (Protobuf field number 2; repeated=False) |
| `DisplacementDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`displacement: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementCombinedProperties` (Protobuf field number 3; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementSpecification` (Protobuf field number 4; repeated=False) |
| `DisplacementRotationCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`displacement_properties: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementRotationProperties` (Protobuf field number 2; repeated=False) |
| `DisplacementRotationProperties` | `rotation: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 2; repeated=False) |
| `DisplacementTranslationCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`displacement_properties: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementTranslationProperties` (Protobuf field number 2; repeated=False) |
| `DisplacementTranslationProperties` | `displacement: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.displacement.DisplacementDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.flow_pb2`

| Message | Fields |
| --- | --- |
| `FlowDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`specification: ansys.api.discovery.v1.physics.conditions.flow.FlowSpecificationDefinition` (Protobuf field number 3; repeated=False)<br>`direction: ansys.api.discovery.v1.physics.conditions.flow.FlowDirectionDefinition` (Protobuf field number 4; repeated=False)<br>`speed: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`pressure: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`mass_flow: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`thermal_properties: ansys.api.discovery.v1.physics.conditions.flow.FlowThermalProperties` (Protobuf field number 8; repeated=False)<br>`is_swirling: bool` (Protobuf field number 9; repeated=False)<br>`rotational_speed: ansys.api.discovery.v1.Quantity` (Protobuf field number 10; repeated=False)<br>`inlet_flow_components_velocity: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 11; repeated=False) |
| `FlowMassFlowInletCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`mass_flow_inlet: ansys.api.discovery.v1.physics.conditions.flow.MassFlowInletProperties` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowInletCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.flow.FlowMassFlowInletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowInletDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`mass_flow_inlet: ansys.api.discovery.v1.physics.conditions.flow.MassFlowInletProperties` (Protobuf field number 3; repeated=False) |
| `FlowMassFlowOutletCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`mass_flow_outlet: ansys.api.discovery.v1.physics.conditions.flow.MassFlowOutletProperties` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowOutletCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.flow.FlowMassFlowOutletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowMassFlowOutletDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`mass_flow_outlet: ansys.api.discovery.v1.physics.conditions.flow.MassFlowOutletProperties` (Protobuf field number 3; repeated=False) |
| `FlowPressureInletCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`pressure_inlet: ansys.api.discovery.v1.physics.conditions.flow.PressureInletProperties` (Protobuf field number 2; repeated=False) |
| `FlowPressureInletCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.flow.FlowPressureInletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowPressureInletDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`pressure_inlet: ansys.api.discovery.v1.physics.conditions.flow.PressureInletProperties` (Protobuf field number 3; repeated=False) |
| `FlowPressureOutletCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`pressure_outlet: ansys.api.discovery.v1.physics.conditions.flow.PressureOutletProperties` (Protobuf field number 2; repeated=False) |
| `FlowPressureOutletCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.flow.FlowPressureOutletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowPressureOutletDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`pressure_outlet: ansys.api.discovery.v1.physics.conditions.flow.PressureOutletProperties` (Protobuf field number 3; repeated=False) |
| `FlowThermalProperties` | `is_thermal: bool` (Protobuf field number 1; repeated=False)<br>`temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `FlowVelocityInletCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`velocity_inlet: ansys.api.discovery.v1.physics.conditions.flow.VelocityInletProperties` (Protobuf field number 4; repeated=False) |
| `FlowVelocityInletCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.flow.FlowVelocityInletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowVelocityInletDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`velocity_inlet: ansys.api.discovery.v1.physics.conditions.flow.VelocityInletProperties` (Protobuf field number 3; repeated=False) |
| `FlowVelocityOutletCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`velocity_outlet: ansys.api.discovery.v1.physics.conditions.flow.VelocityOutletProperties` (Protobuf field number 2; repeated=False) |
| `FlowVelocityOutletCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.flow.FlowVelocityOutletDefinition` (Protobuf field number 2; repeated=False) |
| `FlowVelocityOutletDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`velocity_outlet: ansys.api.discovery.v1.physics.conditions.flow.VelocityOutletProperties` (Protobuf field number 3; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.flow.FlowDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.flow.FlowDefinition` (Protobuf field number 2; repeated=False) |
| `MassFlowInletProperties` | `mass_flow: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v1.physics.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False) |
| `MassFlowOutletProperties` | `mass_flow: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `PressureInletProperties` | `pressure: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v1.physics.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False) |
| `PressureOutletProperties` | `pressure: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v1.physics.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False) |
| `SetFlowDirectionRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.discovery.v1.physics.conditions.flow.FlowDirectionDefinition` (Protobuf field number 2; repeated=False)<br>`reset_to_default_subtype: bool` (Protobuf field number 3; repeated=False) |
| `SetFlowSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.conditions.flow.FlowSpecificationDefinition` (Protobuf field number 2; repeated=False) |
| `VelocityInletProperties` | `speed: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`thermal_properties: ansys.api.discovery.v1.physics.conditions.flow.FlowThermalProperties` (Protobuf field number 2; repeated=False)<br>`is_swirling: bool` (Protobuf field number 3; repeated=False)<br>`rotational_speed: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`inlet_flow_components_velocity: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 5; repeated=False) |
| `VelocityOutletProperties` | `speed: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.fluidinitialtemperature_pb2`

| Message | Fields |
| --- | --- |
| `FluidInitialTemperatureDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.fluidinitialtemperature.FluidInitialTemperatureDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.force_pb2`

| Message | Fields |
| --- | --- |
| `ForceDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`force_specification: ansys.api.discovery.v1.physics.conditions.force.ForceSpecification` (Protobuf field number 3; repeated=False)<br>`magnitude_definition: ansys.api.discovery.v1.physics.conditions.force.ForceMagnitudeDefinition` (Protobuf field number 4; repeated=False)<br>`force: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`force_components: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 6; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 7; repeated=False) |
| `ForceDistributedAreaCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`force_properties: ansys.api.discovery.v1.physics.conditions.force.ForceDistributedProperties` (Protobuf field number 2; repeated=False) |
| `ForceDistributedAreaCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.force.ForceDistributedDefinition` (Protobuf field number 2; repeated=False) |
| `ForceDistributedDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`force_distributed: ansys.api.discovery.v1.physics.conditions.force.ForceDistributedProperties` (Protobuf field number 3; repeated=False)<br>`magnitude_definition: ansys.api.discovery.v1.physics.conditions.force.ForceMagnitudeDefinition` (Protobuf field number 4; repeated=False)<br>`force_specification: ansys.api.discovery.v1.physics.conditions.force.ForceSpecification` (Protobuf field number 5; repeated=False) |
| `ForceDistributedProperties` | `force: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`force_components: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 2; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 3; repeated=False) |
| `ForceDistributedTotalCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`force_properties: ansys.api.discovery.v1.physics.conditions.force.ForceDistributedProperties` (Protobuf field number 2; repeated=False) |
| `ForceDistributedTotalCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.force.ForceDistributedDefinition` (Protobuf field number 2; repeated=False) |
| `ForceTorqueCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`force_properties: ansys.api.discovery.v1.physics.conditions.force.ForceTorqueProperties` (Protobuf field number 2; repeated=False) |
| `ForceTorqueCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.force.ForceTorqueDefinition` (Protobuf field number 2; repeated=False) |
| `ForceTorqueDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`force_torque: ansys.api.discovery.v1.physics.conditions.force.ForceTorqueProperties` (Protobuf field number 3; repeated=False)<br>`force_specification: ansys.api.discovery.v1.physics.conditions.force.ForceSpecification` (Protobuf field number 4; repeated=False) |
| `ForceTorqueProperties` | `force: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`force_components: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.force.ForceDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.force.ForceDefinition` (Protobuf field number 2; repeated=False) |
| `SetForceMagnitudeDefinitionRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`force_magnitude_definition: ansys.api.discovery.v1.physics.conditions.force.ForceMagnitudeDefinition` (Protobuf field number 2; repeated=False) |
| `SetForceSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`force_specification: ansys.api.discovery.v1.physics.conditions.force.ForceSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.gravity_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.gravity.GravityDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.gravity.GravityDefinition` (Protobuf field number 2; repeated=False) |
| `GravityDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`gravity: ansys.api.discovery.v1.physics.conditions.gravity.GravityProperties` (Protobuf field number 3; repeated=False) |
| `GravityProperties` | `acceleration: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`include_buoyancy: bool` (Protobuf field number 2; repeated=False)<br>`include_self_weight: bool` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.heat_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.heat.HeatDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.heat.HeatDefinition` (Protobuf field number 2; repeated=False) |
| `HeatCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`heat: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `HeatDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`total_heat: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`heat_per_unitvolume: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`heat_per_unitarea: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`heat_specification: ansys.api.discovery.v1.physics.conditions.heat.HeatSpecification` (Protobuf field number 6; repeated=False) |
| `HeatPerAreaDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`heat_per_unitarea: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `HeatPerVolumeDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`heat_per_unitvolume: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `HeatSurfaceDistributedCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.heat.HeatPerAreaDefinition` (Protobuf field number 2; repeated=False) |
| `HeatTotalCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.heat.HeatTotalDefinition` (Protobuf field number 2; repeated=False) |
| `HeatTotalDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`total_heat: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `HeatVolumetricDistributedCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.heat.HeatPerVolumeDefinition` (Protobuf field number 2; repeated=False) |
| `SetHeatSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`heat_specification: ansys.api.discovery.v1.physics.conditions.heat.HeatSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.insulated_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.insulated.InsulatedDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.insulated.InsulatedDefinition` (Protobuf field number 2; repeated=False) |
| `InsulatedCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False) |
| `InsulatedCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.insulated.InsulatedDefinition` (Protobuf field number 2; repeated=False) |
| `InsulatedDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |

### `ansys.api.discovery.v1.physics.conditions.localfidelity_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityDefinition` (Protobuf field number 2; repeated=False) |
| `LocalFidelityCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`local_fidelity_properties: ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityProperties` (Protobuf field number 2; repeated=False) |
| `LocalFidelityCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityDefinition` (Protobuf field number 2; repeated=False) |
| `LocalFidelityDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`local_fidelity: ansys.api.discovery.v1.physics.conditions.localfidelity.LocalFidelityProperties` (Protobuf field number 3; repeated=False) |
| `LocalFidelityProperties` | `local_fidelity_magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.mass_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.mass.MassDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.mass.MassDefinition` (Protobuf field number 2; repeated=False) |
| `MassCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`mass_properties: ansys.api.discovery.v1.physics.conditions.mass.MassProperties` (Protobuf field number 2; repeated=False) |
| `MassCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.mass.MassDefinition` (Protobuf field number 2; repeated=False) |
| `MassDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`mass: ansys.api.discovery.v1.physics.conditions.mass.MassProperties` (Protobuf field number 3; repeated=False)<br>`use_remote_point: bool` (Protobuf field number 4; repeated=False) |
| `MassProperties` | `mass_magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.moment_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.moment.MomentDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.moment.MomentDefinition` (Protobuf field number 2; repeated=False) |
| `MomentCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`moment_properties: ansys.api.discovery.v1.physics.conditions.moment.MomentProperties` (Protobuf field number 2; repeated=False) |
| `MomentCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.moment.MomentDefinition` (Protobuf field number 2; repeated=False) |
| `MomentDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`local: ansys.api.discovery.v1.physics.conditions.moment.MomentProperties` (Protobuf field number 3; repeated=False)<br>`global: ansys.api.discovery.v1.physics.conditions.moment.MomentProperties` (Protobuf field number 4; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.conditions.moment.MomentSpecification` (Protobuf field number 5; repeated=False) |
| `MomentProperties` | `moment: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 1; repeated=False) |
| `SetMomentSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`moment_specification: ansys.api.discovery.v1.physics.conditions.moment.MomentSpecification` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.operatingpressure_pb2`

| Message | Fields |
| --- | --- |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.operatingpressure.OperatingPressureDefinition` (Protobuf field number 2; repeated=False) |
| `OperatingPressureDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.porous_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.porous.PorousDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.porous.PorousDefinition` (Protobuf field number 2; repeated=False) |
| `PorousCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`porous_properties: ansys.api.discovery.v1.physics.conditions.porous.PorousProperties` (Protobuf field number 2; repeated=False)<br>`streamwise_flow_direction_reference: ansys.api.discovery.v1.physics.LocationIdentifier` (Protobuf field number 3; repeated=False) |
| `PorousCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.porous.PorousDefinition` (Protobuf field number 2; repeated=False) |
| `PorousDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`porous_properties: ansys.api.discovery.v1.physics.conditions.porous.PorousProperties` (Protobuf field number 3; repeated=False)<br>`porous_specification: ansys.api.discovery.v1.physics.conditions.porous.PorousSpecification` (Protobuf field number 4; repeated=False)<br>`streamwise_flow_direction_reference: ansys.api.discovery.v1.physics.LocationIdentifier` (Protobuf field number 5; repeated=False) |
| `PorousProperties` | `coefficients: ansys.api.discovery.v1.physics.conditions.porous.ResistanceCoeffients` (Protobuf field number 1; repeated=False)<br>`solid_properties: ansys.api.discovery.v1.physics.conditions.porous.SolidProperties` (Protobuf field number 2; repeated=False) |
| `ResistanceCoeffients` | `viscous_streamwise: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`inertial_streamwise: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`viscous_primary: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`inertial_primary: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`viscous_secondary: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`inertial_secondary: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False) |
| `SetPorousSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.conditions.porous.PorousSpecification` (Protobuf field number 2; repeated=False) |
| `SolidProperties` | `porosity: double` (Protobuf field number 1; repeated=False)<br>`density: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`isotropic_thermal_conductivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`specific_heat: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.pressure_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.pressure.PressureDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.pressure.PressureDefinition` (Protobuf field number 2; repeated=False) |
| `PressureCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`pressure_properties: ansys.api.discovery.v1.physics.conditions.pressure.PressureProperties` (Protobuf field number 2; repeated=False) |
| `PressureCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.pressure.PressureDefinition` (Protobuf field number 2; repeated=False) |
| `PressureDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`pressure: ansys.api.discovery.v1.physics.conditions.pressure.PressureProperties` (Protobuf field number 3; repeated=False) |
| `PressureProperties` | `pressure_magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.rotatingfluidzone_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneDefinition` (Protobuf field number 2; repeated=False) |
| `RotatingFluidZoneCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`rotating_fluid_zone_properties: ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneProperties` (Protobuf field number 4; repeated=False) |
| `RotatingFluidZoneCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneDefinition` (Protobuf field number 2; repeated=False) |
| `RotatingFluidZoneDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`rotating_fluid_zone_properties: ansys.api.discovery.v1.physics.conditions.rotatingfluidzone.RotatingFluidZoneProperties` (Protobuf field number 3; repeated=False) |
| `RotatingFluidZoneProperties` | `rotational_velocity: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.solidtemperature_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureDefinition` (Protobuf field number 2; repeated=False) |
| `TemperatureCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False) |
| `TemperatureCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.solidtemperature.TemperatureDefinition` (Protobuf field number 2; repeated=False) |
| `TemperatureDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.springpreload_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadDefinition` (Protobuf field number 2; repeated=False) |
| `SetSpringPreloadSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`specification: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadSpecification` (Protobuf field number 2; repeated=False) |
| `SetSpringPreloadTypeRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`type: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadType` (Protobuf field number 2; repeated=False) |
| `SpringPreloadCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadDefinition` (Protobuf field number 2; repeated=False) |
| `SpringPreloadDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`side1_locations: string` (Protobuf field number 2; repeated=True)<br>`side2_locations: string` (Protobuf field number 3; repeated=True)<br>`specification: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadSpecification` (Protobuf field number 4; repeated=False)<br>`longitudinal_stiffness_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadLongitudinalStiffnessProperties` (Protobuf field number 5; repeated=False)<br>`torsional_stiffness_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadTorsionalStiffnessProperties` (Protobuf field number 6; repeated=False)<br>`preload_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadProperties` (Protobuf field number 7; repeated=False) |
| `SpringPreloadLongitudinalCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`longitudinal_stiffness_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadLongitudinalStiffnessProperties` (Protobuf field number 3; repeated=False)<br>`preload_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadProperties` (Protobuf field number 4; repeated=False) |
| `SpringPreloadLongitudinalStiffnessProperties` | `longitudinal_stiffness: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |
| `SpringPreloadProperties` | `type: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadType` (Protobuf field number 1; repeated=False)<br>`preload_force: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`preload_length: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`preload_torque: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`preload_rotation: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False) |
| `SpringPreloadTorsionalCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`torsional_stiffness_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadTorsionalStiffnessProperties` (Protobuf field number 3; repeated=False)<br>`preload_properties: ansys.api.discovery.v1.physics.conditions.springpreload.SpringPreloadProperties` (Protobuf field number 4; repeated=False) |
| `SpringPreloadTorsionalStiffnessProperties` | `torsional_stiffness: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.support_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.support.SupportDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.support.SupportDefinition` (Protobuf field number 2; repeated=False) |
| `SetSupportSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`support_specification: ansys.api.discovery.v1.physics.conditions.support.SupportSpecification` (Protobuf field number 2; repeated=False) |
| `SupportDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`support_type: ansys.api.discovery.v1.physics.conditions.support.SupportSpecification` (Protobuf field number 3; repeated=False)<br>`displacement: ansys.api.discovery.v1.TensorOfOptionalQuantities` (Protobuf field number 4; repeated=False) |
| `SupportDisplacedCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`support_displaced: ansys.api.discovery.v1.physics.conditions.support.SupportDisplacedProperties` (Protobuf field number 2; repeated=False) |
| `SupportDisplacedCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.support.SupportDisplacedDefinition` (Protobuf field number 2; repeated=False) |
| `SupportDisplacedDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`support_type: ansys.api.discovery.v1.physics.conditions.support.SupportSpecification` (Protobuf field number 3; repeated=False)<br>`displacement: ansys.api.discovery.v1.TensorOfOptionalQuantities` (Protobuf field number 4; repeated=False) |
| `SupportDisplacedProperties` | `displacement: ansys.api.discovery.v1.TensorOfOptionalQuantities` (Protobuf field number 1; repeated=False) |
| `SupportGeneralCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False) |
| `SupportGeneralCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.support.SupportGeneralDefinition` (Protobuf field number 2; repeated=False) |
| `SupportGeneralDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`support_type: ansys.api.discovery.v1.physics.conditions.support.SupportSpecification` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.symmetry_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.symmetry.SymmetryDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.symmetry.SymmetryDefinition` (Protobuf field number 2; repeated=False) |
| `SymmetryCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False) |
| `SymmetryCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.symmetry.SymmetryDefinition` (Protobuf field number 2; repeated=False) |
| `SymmetryDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True) |

### `ansys.api.discovery.v1.physics.conditions.velocity_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.velocity.VelocityDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.velocity.VelocityDefinition` (Protobuf field number 2; repeated=False) |
| `VelocityCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`velocity_properties: ansys.api.discovery.v1.physics.conditions.velocity.VelocityProperties` (Protobuf field number 2; repeated=False) |
| `VelocityCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.velocity.VelocityDefinition` (Protobuf field number 2; repeated=False) |
| `VelocityDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`velocity: ansys.api.discovery.v1.physics.conditions.velocity.VelocityProperties` (Protobuf field number 3; repeated=False) |
| `VelocityProperties` | `velocity: ansys.api.discovery.v1.VectorOfOptionalQuantities` (Protobuf field number 1; repeated=False)<br>`remote_point: ansys.api.discovery.v1.OptionalVector` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.voltage_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.voltage.VoltageDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.voltage.VoltageDefinition` (Protobuf field number 2; repeated=False) |
| `VoltageCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 1; repeated=False)<br>`voltage_properties: ansys.api.discovery.v1.physics.conditions.voltage.VoltageProperties` (Protobuf field number 2; repeated=False) |
| `VoltageCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.voltage.VoltageDefinition` (Protobuf field number 2; repeated=False) |
| `VoltageDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`voltage: ansys.api.discovery.v1.physics.conditions.voltage.VoltageProperties` (Protobuf field number 3; repeated=False) |
| `VoltageProperties` | `voltage_magnitude: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.conditions.wall_pb2`

| Message | Fields |
| --- | --- |
| `FreeSlipProperties` | `wall_thermal_option_enabled: bool` (Protobuf field number 1; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v1.physics.conditions.wall.WallThermalProperties` (Protobuf field number 2; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.conditions.wall.WallDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.conditions.wall.WallDefinition` (Protobuf field number 2; repeated=False) |
| `RotationProperties` | `rotational_velocity: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`wall_thermal_option_enabled: bool` (Protobuf field number 2; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v1.physics.conditions.wall.WallThermalProperties` (Protobuf field number 3; repeated=False) |
| `SetWallSpecificationRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`wall_specification: ansys.api.discovery.v1.physics.conditions.wall.WallSpecification` (Protobuf field number 2; repeated=False) |
| `SetWallThermalOptionRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`wall_thermal_option: ansys.api.discovery.v1.physics.conditions.wall.WallThermalOption` (Protobuf field number 2; repeated=False)<br>`is_external_radiation_enabled: bool` (Protobuf field number 3; repeated=False) |
| `StationaryProperties` | `wall_thermal_option_enabled: bool` (Protobuf field number 1; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v1.physics.conditions.wall.WallThermalProperties` (Protobuf field number 2; repeated=False) |
| `TranslationProperties` | `wall_thermal_option_enabled: bool` (Protobuf field number 1; repeated=False)<br>`translational_velocity: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 2; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v1.physics.conditions.wall.WallThermalProperties` (Protobuf field number 3; repeated=False) |
| `WallDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`specification: ansys.api.discovery.v1.physics.conditions.wall.WallSpecification` (Protobuf field number 3; repeated=False)<br>`wall_thermal_option_enabled: bool` (Protobuf field number 4; repeated=False)<br>`wall_thermal_properties: ansys.api.discovery.v1.physics.conditions.wall.WallThermalProperties` (Protobuf field number 5; repeated=False)<br>`rotational_velocity: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`translational_velocity: ansys.api.discovery.v1.QuantityVector` (Protobuf field number 7; repeated=False) |
| `WallFreeSlipCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`freeslip_properties: ansys.api.discovery.v1.physics.conditions.wall.FreeSlipProperties` (Protobuf field number 4; repeated=False) |
| `WallFreeSlipCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.wall.WallFreeSlipDefinition` (Protobuf field number 2; repeated=False) |
| `WallFreeSlipDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`free_slip_properties: ansys.api.discovery.v1.physics.conditions.wall.FreeSlipProperties` (Protobuf field number 3; repeated=False) |
| `WallRotationCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`rotating_properties: ansys.api.discovery.v1.physics.conditions.wall.RotationProperties` (Protobuf field number 4; repeated=False) |
| `WallRotationCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.wall.WallRotationDefinition` (Protobuf field number 2; repeated=False) |
| `WallRotationDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`rotation_properties: ansys.api.discovery.v1.physics.conditions.wall.RotationProperties` (Protobuf field number 3; repeated=False) |
| `WallStationaryCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`stationary_properties: ansys.api.discovery.v1.physics.conditions.wall.StationaryProperties` (Protobuf field number 4; repeated=False) |
| `WallStationaryCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.wall.WallStationaryDefinition` (Protobuf field number 2; repeated=False) |
| `WallStationaryDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`stationary_properties: ansys.api.discovery.v1.physics.conditions.wall.StationaryProperties` (Protobuf field number 3; repeated=False) |
| `WallThermalProperties` | `wall_thermal_option: ansys.api.discovery.v1.physics.conditions.wall.WallThermalOption` (Protobuf field number 1; repeated=False)<br>`internal_emissivity: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 2; repeated=False)<br>`external_temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`convection_coefficient: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`heatflux: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`heatflow: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`temperature: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`external_emissivity: ansys.api.discovery.v1.OptionalQuantity` (Protobuf field number 8; repeated=False) |
| `WallTranslationCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.ScopedCreationData` (Protobuf field number 2; repeated=False)<br>`translating_properties: ansys.api.discovery.v1.physics.conditions.wall.TranslationProperties` (Protobuf field number 4; repeated=False) |
| `WallTranslationCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`as_created_data: ansys.api.discovery.v1.physics.conditions.wall.WallTranslationDefinition` (Protobuf field number 2; repeated=False) |
| `WallTranslationDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`locations: string` (Protobuf field number 2; repeated=True)<br>`translation_properties: ansys.api.discovery.v1.physics.conditions.wall.TranslationProperties` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.physics.connections.contact_pb2`

| Message | Fields |
| --- | --- |
| `ChangeContactPairRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`contact_pairs: ansys.api.discovery.v1.physics.ContactPairs` (Protobuf field number 2; repeated=False) |
| `ContactCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`contact_properties: ansys.api.discovery.v1.physics.ContactProperties` (Protobuf field number 2; repeated=False) |
| `ContactCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.connections.contact.ContactDefinition` (Protobuf field number 2; repeated=False) |
| `ContactDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`side1_locations: string` (Protobuf field number 2; repeated=True)<br>`side2_locations: string` (Protobuf field number 3; repeated=True)<br>`contact: ansys.api.discovery.v1.physics.ContactProperties` (Protobuf field number 4; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.connections.contact.ContactDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.connections.contact.ContactDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.connections.contactgroup_pb2`

| Message | Fields |
| --- | --- |
| `ContactGroupDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`side1_locations: string` (Protobuf field number 2; repeated=True)<br>`side2_locations: string` (Protobuf field number 3; repeated=True)<br>`contact: ansys.api.discovery.v1.physics.ContactProperties` (Protobuf field number 4; repeated=False) |
| `ConvertContactGroupChangeRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`contact_group_type: ansys.api.discovery.v1.physics.connections.contactgroup.ContactGroupConversionType` (Protobuf field number 2; repeated=False)<br>`contact_pairs: ansys.api.discovery.v1.physics.ContactPairs` (Protobuf field number 3; repeated=False)<br>`idealize: bool` (Protobuf field number 4; repeated=False)<br>`friction_coefficient: double` (Protobuf field number 5; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.connections.contactgroup.ContactGroupDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.connections.contactgroup.ContactGroupDefinition` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.connections.fluidinterface_pb2`

| Message | Fields |
| --- | --- |
| `ChangeFluidInterfaceConductanceMethod` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`thermal_conductivity_method: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceFaceThermalConductanceMethod` (Protobuf field number 2; repeated=False) |
| `FluidInterfaceDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`fluid_interface_properties: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceProperties` (Protobuf field number 2; repeated=False) |
| `FluidInterfaceProperties` | `interface_type: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceType` (Protobuf field number 1; repeated=False)<br>`face_grouping_method: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceFaceGroupingMethod` (Protobuf field number 2; repeated=False)<br>`thermal_conductance_method: ansys.api.discovery.v1.ConductanceOptionType` (Protobuf field number 3; repeated=False)<br>`detection_distance_high: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`face_overlap_allowance: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`thermal_material: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 6; repeated=False)<br>`thermal_conductance: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`thermal_conductivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 8; repeated=False)<br>`thermal_thickness: ansys.api.discovery.v1.Quantity` (Protobuf field number 9; repeated=False)<br>`internal_radiation_input_enabled: bool` (Protobuf field number 10; repeated=False)<br>`internal_emissivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 11; repeated=False) |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceDefinition` (Protobuf field number 2; repeated=False) |
| `SetFluidInterfaceFaceGroupingMethodRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`face_grouping_method: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceFaceGroupingMethod` (Protobuf field number 2; repeated=False) |
| `SetFluidInterfaceTypeRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`interface_type: ansys.api.discovery.v1.physics.connections.fluidinterface.FluidInterfaceType` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.connections.joint_pb2`

| Message | Fields |
| --- | --- |
| `GetAllResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definitions: ansys.api.discovery.v1.physics.connections.joint.JointDefinition` (Protobuf field number 2; repeated=True) |
| `GetSingleResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False)<br>`entity_definition: ansys.api.discovery.v1.physics.connections.joint.JointDefinition` (Protobuf field number 2; repeated=False) |
| `JointCreationRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`joint_properties: ansys.api.discovery.v1.physics.connections.joint.JointProperties` (Protobuf field number 2; repeated=False) |
| `JointCreationResponse` | `creation_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`condition_data: ansys.api.discovery.v1.physics.connections.joint.JointDefinition` (Protobuf field number 2; repeated=False) |
| `JointDefinition` | `base_properties: ansys.api.discovery.v1.physics.PhysicsEntityBaseProperties` (Protobuf field number 1; repeated=False)<br>`side1_locations: string` (Protobuf field number 2; repeated=True)<br>`side2_locations: string` (Protobuf field number 3; repeated=True)<br>`joint: ansys.api.discovery.v1.physics.connections.joint.JointProperties` (Protobuf field number 4; repeated=False) |
| `JointProperties` | `joint_type: ansys.api.discovery.v1.physics.connections.joint.JointType` (Protobuf field number 1; repeated=False) |
| `SetJointTypeRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`joint_type: ansys.api.discovery.v1.physics.connections.joint.JointType` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.parameterization.definedvariation_pb2`

| Message | Fields |
| --- | --- |
| `CreateRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `CreateResponse` | `variation: ansys.api.discovery.v1.physics.Variation` (Protobuf field number 1; repeated=False) |
| `DeleteScriptRequest` | — |
| `DeleteScriptResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `GetAllRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `defined_variations: ansys.api.discovery.v1.physics.Variation` (Protobuf field number 2; repeated=True) |
| `GetCurrentRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetCurrentResponse` | `variation: ansys.api.discovery.v1.physics.Variation` (Protobuf field number 1; repeated=False) |
| `GetInputRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`input_parameter_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 3; repeated=False) |
| `GetInputResponse` | `input: ansys.api.discovery.v1.physics.InputParameter` (Protobuf field number 1; repeated=False) |
| `GetOutputRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`output_parameter_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 3; repeated=False) |
| `GetOutputResponse` | `output: ansys.api.discovery.v1.physics.OutputParameter` (Protobuf field number 1; repeated=False) |
| `GetRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetResponse` | `variation: ansys.api.discovery.v1.physics.Variation` (Protobuf field number 1; repeated=False) |
| `GetScriptRequest` | — |
| `GetScriptResponse` | `script: string` (Protobuf field number 1; repeated=False) |
| `GetStarredRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetStarredResponse` | `variations: ansys.api.discovery.v1.physics.Variation` (Protobuf field number 1; repeated=True) |
| `IsSolvingRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `IsSolvingResponse` | `is_solving: bool` (Protobuf field number 1; repeated=False) |
| `SetCurrentRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `SetCurrentResponse` | `success: bool` (Protobuf field number 1; repeated=False) |
| `SetScriptRequest` | `script: string` (Protobuf field number 1; repeated=False) |
| `SetScriptResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |
| `SetStarredRequest` | `variation_ids: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=True)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`starred: bool` (Protobuf field number 3; repeated=False) |
| `SetStarredResponse` | — |

### `ansys.api.discovery.v1.physics.parameterization.parameter_pb2`

| Message | Fields |
| --- | --- |
| `GetAllInputsRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetAllInputsResponse` | `input_parameters: ansys.api.discovery.v1.physics.InputParameter` (Protobuf field number 1; repeated=True) |
| `GetAllOutputsRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False) |
| `GetAllOutputsResponse` | `output_parameters: ansys.api.discovery.v1.physics.OutputParameter` (Protobuf field number 1; repeated=True) |
| `SetInputValueRequest` | `variation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`input_parameter_label: string` (Protobuf field number 3; repeated=False)<br>`value: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`material: ansys.api.discovery.v1.physics.ParameterMaterial` (Protobuf field number 5; repeated=False) |
| `SetInputValueResponse` | `input: ansys.api.discovery.v1.physics.InputParameter` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.physics.physicsentity_pb2`

| Message | Fields |
| --- | --- |
| `DeleteRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `SetNameRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`new_name: string` (Protobuf field number 2; repeated=False) |
| `SetSuppressionStateRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`is_suppressed: bool` (Protobuf field number 2; repeated=False) |

### `ansys.api.discovery.v1.physics.physicsmessages_pb2`

| Message | Fields |
| --- | --- |
| `CommandRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False) |
| `ContactPair` | `item1: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`item2: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=True) |
| `ContactPairs` | `contact_pair: ansys.api.discovery.v1.physics.ContactPair` (Protobuf field number 1; repeated=True) |
| `ContactProperties` | `contact_type: ansys.api.discovery.v1.ContactType` (Protobuf field number 1; repeated=False)<br>`contact_pairs: ansys.api.discovery.v1.physics.ContactPairs` (Protobuf field number 2; repeated=False)<br>`friction_coefficient: double` (Protobuf field number 3; repeated=False)<br>`stiffness_factor: double` (Protobuf field number 4; repeated=False)<br>`detection_radius_factor: double` (Protobuf field number 5; repeated=False)<br>`offset: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`shear_strenght: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`tensile_strength: ansys.api.discovery.v1.Quantity` (Protobuf field number 8; repeated=False)<br>`are_strength_limits_set: bool` (Protobuf field number 9; repeated=False)<br>`adjust_gap_or_overlap: bool` (Protobuf field number 10; repeated=False)<br>`make_just_touching: bool` (Protobuf field number 11; repeated=False)<br>`idealize: bool` (Protobuf field number 12; repeated=False)<br>`specify_thermal_conductance: bool` (Protobuf field number 13; repeated=False)<br>`specify_electric_conductance: bool` (Protobuf field number 14; repeated=False)<br>`thermal_contact_conductance: ansys.api.discovery.v1.Quantity` (Protobuf field number 15; repeated=False)<br>`thermal_contact_conductivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 16; repeated=False)<br>`thermal_conductance_thickness: ansys.api.discovery.v1.Quantity` (Protobuf field number 17; repeated=False)<br>`electrical_contact_conductance: ansys.api.discovery.v1.Quantity` (Protobuf field number 18; repeated=False)<br>`electrical_contact_conductivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 19; repeated=False)<br>`electrical_conductance_thickness: ansys.api.discovery.v1.Quantity` (Protobuf field number 20; repeated=False)<br>`thermal_conductance_option: ansys.api.discovery.v1.ConductanceOptionType` (Protobuf field number 21; repeated=False)<br>`electric_conductance_option: ansys.api.discovery.v1.ConductanceOptionType` (Protobuf field number 22; repeated=False) |
| `DoubleSidedScopedCreationData` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`side1_locations: ansys.api.discovery.v1.physics.LocationIdentifier` (Protobuf field number 3; repeated=False)<br>`side2_locations: ansys.api.discovery.v1.physics.LocationIdentifier` (Protobuf field number 4; repeated=False) |
| `InputParameter` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`quantity: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`material: ansys.api.discovery.v1.physics.ParameterMaterial` (Protobuf field number 5; repeated=False)<br>`input_type: ansys.api.discovery.v1.InputParameterType` (Protobuf field number 6; repeated=False)<br>`parent_object_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 7; repeated=False)<br>`parameter_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 8; repeated=False) |
| `LocationIdentifier` | `location_ids: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=True)<br>`location_type: ansys.api.discovery.v1.LocationType` (Protobuf field number 2; repeated=False) |
| `MaterialAppearanceProperties` | `alpha: int32` (Protobuf field number 1; repeated=False)<br>`red: int32` (Protobuf field number 2; repeated=False)<br>`green: int32` (Protobuf field number 3; repeated=False)<br>`blue: int32` (Protobuf field number 4; repeated=False)<br>`metallic_finish: int32` (Protobuf field number 5; repeated=False)<br>`roughness: int32` (Protobuf field number 6; repeated=False)<br>`light_transmittance: int32` (Protobuf field number 7; repeated=False) |
| `MaterialDefinition` | `id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`label: string` (Protobuf field number 2; repeated=False)<br>`physical_properties: ansys.api.discovery.v1.physics.MaterialPhysicalProperties` (Protobuf field number 3; repeated=False)<br>`mechanical_properties: ansys.api.discovery.v1.physics.MaterialMechanicalProperties` (Protobuf field number 4; repeated=False)<br>`thermal_properties: ansys.api.discovery.v1.physics.MaterialThermalProperties` (Protobuf field number 5; repeated=False)<br>`electromagnetic_properties: ansys.api.discovery.v1.physics.MaterialElectromagneticProperties` (Protobuf field number 6; repeated=False)<br>`environmental_properties: ansys.api.discovery.v1.physics.MaterialEnvironmentalProperties` (Protobuf field number 7; repeated=False)<br>`appearance_properties: ansys.api.discovery.v1.physics.MaterialAppearanceProperties` (Protobuf field number 8; repeated=False)<br>`material_state: ansys.api.discovery.v1.physics.MaterialState` (Protobuf field number 9; repeated=False)<br>`material_source: ansys.api.discovery.v1.physics.MaterialSource` (Protobuf field number 10; repeated=False) |
| `MaterialElectromagneticProperties` | `electric_conductivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`relative_permittivity: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`relative_permeability: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`electric_loss_tangent: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`magnetic_loss_tangent: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`electric_conductivity_table: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 6; repeated=False) |
| `MaterialEnvironmentalProperties` | `embodied_energy: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`co2_footprint: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`recycle: bool` (Protobuf field number 3; repeated=False) |
| `MaterialInternalRadiationProperties` | `absorption_coefficient: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`scattering_coefficient: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`refractive_index: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False) |
| `MaterialMechanicalProperties` | `youngs_modulus: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`poissons_ratio: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`shear_modulues: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`bulk_modulus: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`youngs_modulus_table: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 5; repeated=False) |
| `MaterialPhysicalProperties` | `density: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`viscosity: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`molar_mass: ansys.api.discovery.v1.Quantity` (Protobuf field number 3; repeated=False)<br>`tensile_yeld_strength: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`tensile_ultimate_yeld_strength: ansys.api.discovery.v1.Quantity` (Protobuf field number 5; repeated=False)<br>`compressive_yeld_strength: ansys.api.discovery.v1.Quantity` (Protobuf field number 6; repeated=False)<br>`compressive_ultimate_yeld_strength: ansys.api.discovery.v1.Quantity` (Protobuf field number 7; repeated=False)<br>`density_table: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 8; repeated=False) |
| `MaterialSource` | `source_material_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`database_key: string` (Protobuf field number 2; repeated=False)<br>`history_guid: string` (Protobuf field number 3; repeated=False) |
| `MaterialThermalConductivityProperties` | `thermal_conductivity_specification: ansys.api.discovery.v1.physics.ThermalConductivitySpecification` (Protobuf field number 1; repeated=False)<br>`isotropic_thermal_conductivity: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 2; repeated=False)<br>`orthotropic_thermal_conductivity_x: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 3; repeated=False)<br>`orthotropic_thermal_conductivity_y: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 4; repeated=False)<br>`orthotropic_thermal_conductivity_z: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 5; repeated=False) |
| `MaterialThermalProperties` | `coefficient_of_thermal_expansion: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=False)<br>`specific_heat: ansys.api.discovery.v1.Quantity` (Protobuf field number 2; repeated=False)<br>`thermal_conductivity: ansys.api.discovery.v1.physics.MaterialThermalConductivityProperties` (Protobuf field number 3; repeated=False)<br>`specific_heat_table: ansys.api.discovery.v1.QuantityGenericTable` (Protobuf field number 4; repeated=False)<br>`internal_radiation_properties: ansys.api.discovery.v1.physics.MaterialInternalRadiationProperties` (Protobuf field number 5; repeated=False) |
| `OutputParameter` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 2; repeated=False)<br>`name: string` (Protobuf field number 3; repeated=False)<br>`quantity: ansys.api.discovery.v1.Quantity` (Protobuf field number 4; repeated=False)<br>`parameter_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 5; repeated=False) |
| `ParameterMaterial` | `material_id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`material_label: string` (Protobuf field number 2; repeated=False) |
| `PhysicsEntityBaseProperties` | `id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`parent_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`label: string` (Protobuf field number 3; repeated=False)<br>`suppressed: bool` (Protobuf field number 4; repeated=False) |
| `ScopedCreationData` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 2; repeated=False)<br>`locations: ansys.api.discovery.v1.physics.LocationIdentifier` (Protobuf field number 3; repeated=False) |
| `SetConductanceMethodRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`conductance_type: ansys.api.discovery.v1.ConductanceOptionType` (Protobuf field number 2; repeated=False) |
| `SetContactTypeRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`contact_type: ansys.api.discovery.v1.ContactType` (Protobuf field number 2; repeated=False) |
| `SetDirectionRequest` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`direction: ansys.api.discovery.v1.Direction` (Protobuf field number 2; repeated=False) |
| `SimulationEntity` | `object_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`label: string` (Protobuf field number 2; repeated=False) |
| `Variation` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`name: string` (Protobuf field number 2; repeated=False)<br>`starred: bool` (Protobuf field number 3; repeated=False)<br>`inputs: ansys.api.discovery.v1.physics.InputParameter` (Protobuf field number 4; repeated=True)<br>`outputs: ansys.api.discovery.v1.physics.OutputParameter` (Protobuf field number 5; repeated=True)<br>`simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 6; repeated=False) |

### `ansys.api.discovery.v1.physics.simulation.monitors_pb2`

| Message | Fields |
| --- | --- |
| `CreateMonitorRequest` | `creation_data: ansys.api.discovery.v1.physics.DoubleSidedScopedCreationData` (Protobuf field number 1; repeated=False)<br>`monitor: ansys.api.discovery.v1.physics.simulation.monitors.MonitorProperties` (Protobuf field number 2; repeated=False) |
| `GetAllMonitorsRequest` | — |
| `GetAllMonitorsResponse` | `monitor_definitions: ansys.api.discovery.v1.physics.simulation.monitors.MonitorDefinition` (Protobuf field number 1; repeated=True) |
| `GetMonitorValuesRequest` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False) |
| `GetMonitorValuesResponse` | `monitor_values: ansys.api.discovery.v1.Quantity` (Protobuf field number 1; repeated=True) |
| `MonitorCreationResponse` | `monitor_response: ansys.api.discovery.v1.CreationResponse` (Protobuf field number 1; repeated=False)<br>`monitor: ansys.api.discovery.v1.physics.simulation.monitors.MonitorDefinition` (Protobuf field number 2; repeated=False) |
| `MonitorDefinition` | `id: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 1; repeated=False)<br>`label: string` (Protobuf field number 2; repeated=False)<br>`side1_locations: string` (Protobuf field number 3; repeated=True)<br>`side2_locations: string` (Protobuf field number 4; repeated=True)<br>`monitor: ansys.api.discovery.v1.physics.simulation.monitors.MonitorProperties` (Protobuf field number 5; repeated=False) |
| `MonitorProperties` | `result_variable: ansys.api.discovery.v1.ResultVariable` (Protobuf field number 1; repeated=False)<br>`result_function: ansys.api.discovery.v1.ResultFunction` (Protobuf field number 2; repeated=False)<br>`result_component: ansys.api.discovery.v1.ResultComponent` (Protobuf field number 3; repeated=False) |

### `ansys.api.discovery.v1.physics.simulation.simulations_pb2`

| Message | Fields |
| --- | --- |
| `CreateSimulationRequest` | — |
| `CreateSimulationResponse` | `simulation: ansys.api.discovery.v1.physics.SimulationEntity` (Protobuf field number 1; repeated=False) |
| `GetAllResponse` | `simulations: ansys.api.discovery.v1.physics.SimulationEntity` (Protobuf field number 1; repeated=True) |

### `ansys.api.discovery.v1.physics.simulation.solutions_pb2`

| Message | Fields |
| --- | --- |
| `GetSolverFidelityRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`stage: string` (Protobuf field number 2; repeated=False) |
| `GetSolverFidelityResponse` | `value: double` (Protobuf field number 1; repeated=False) |
| `SetSolverFidelityRequest` | `simulation_stage: ansys.api.discovery.v1.physics.simulation.solutions.GetSolverFidelityRequest` (Protobuf field number 1; repeated=False)<br>`value: double` (Protobuf field number 2; repeated=False) |
| `SetSolverFidelityResponse` | — |
| `SolveExecutionRequest` | `simulation_id: ansys.api.discovery.v1.GuidEntityIdentifier` (Protobuf field number 1; repeated=False)<br>`solver_manager: ansys.api.discovery.v1.physics.simulation.solutions.SolverManager` (Protobuf field number 2; repeated=False)<br>`execute_remotely: bool` (Protobuf field number 3; repeated=False)<br>`variation_id_list: ansys.api.discovery.v1.EntityIdentifier` (Protobuf field number 4; repeated=True) |
| `SolveExecutionResponse` | `command_response: ansys.api.discovery.v1.CommandResponse` (Protobuf field number 1; repeated=False) |

### `ansys.api.discovery.v1.streaming_pb2`

| Message | Fields |
| --- | --- |
| `StreamPackage` | `content_type: string` (Protobuf field number 1; repeated=False)<br>`count: int32` (Protobuf field number 2; repeated=False)<br>`index: int32` (Protobuf field number 3; repeated=False)<br>`total_size: int32` (Protobuf field number 4; repeated=False)<br>`package_size: int32` (Protobuf field number 5; repeated=False)<br>`data: bytes` (Protobuf field number 6; repeated=False) |

## Snapshot counts

- RPC methods: 1422
- Protocol messages: 1742
- Message fields: 4119
