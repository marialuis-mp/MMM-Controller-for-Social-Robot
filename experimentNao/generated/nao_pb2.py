# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: nao.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tnao.proto\"\x06\n\x04Void\";\n\x0eMessageToSpeak\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x18\n\x10\x61nimated_message\x18\x02 \x01(\x08\":\n\x0c\x42odyMovement\x12\x14\n\x0cmovement_tag\x18\x01 \x01(\t\x12\x14\n\x0c\x61synchronous\x18\x02 \x01(\x08\"\'\n\x13\x43oordinatedMovement\x12\x10\n\x08movement\x18\x01 \x01(\t\"8\n\x0c\x46\x61\x63\x65\x44\x65tected\x12\x17\n\x0f\x64\x65tected_or_not\x18\x01 \x01(\x08\x12\x0f\n\x07\x66\x61\x63\x65_id\x18\x02 \x01(\x01\"C\n\rCameraCapture\x12\x13\n\x0b\x62ytes_image\x18\x01 \x01(\x0c\x12\r\n\x05width\x18\x02 \x01(\x03\x12\x0e\n\x06height\x18\x03 \x01(\x03\"2\n\x0eNumericRequest\x12\x0f\n\x07number1\x18\x01 \x01(\x01\x12\x0f\n\x07number2\x18\x02 \x01(\x01\"F\n\x0cSomeResponse\x12\x10\n\x08\x61\x64\x64ition\x18\x01 \x01(\x01\x12\x13\n\x0bsubtraction\x18\x02 \x01(\x01\x12\x0f\n\x07product\x18\x03 \x01(\x01\x32\x8a\x03\n\rNaoController\x12/\n\x0b\x44oSomething\x12\x0f.NumericRequest\x1a\r.SomeResponse\"\x00\x12.\n\x12PrintClientMessage\x12\x0f.MessageToSpeak\x1a\x05.Void\"\x00\x12.\n\x12StartFaceDetection\x12\x05.Void\x1a\r.FaceDetected\"\x00\x30\x01\x12(\n\x0cSaySomething\x12\x0f.MessageToSpeak\x1a\x05.Void\"\x00\x12+\n\x10GetCameraCapture\x12\x05.Void\x1a\x0e.CameraCapture\"\x00\x12-\n\x11\x43hangeSpeechSpeed\x12\x0f.NumericRequest\x1a\x05.Void\"\x00\x12)\n\x0fRunBodyMovement\x12\r.BodyMovement\x1a\x05.Void\"\x00\x12\x37\n\x16RunCoordinatedMovement\x12\x14.CoordinatedMovement\x1a\x05.Void\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'nao_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _VOID._serialized_start=13
  _VOID._serialized_end=19
  _MESSAGETOSPEAK._serialized_start=21
  _MESSAGETOSPEAK._serialized_end=80
  _BODYMOVEMENT._serialized_start=82
  _BODYMOVEMENT._serialized_end=140
  _COORDINATEDMOVEMENT._serialized_start=142
  _COORDINATEDMOVEMENT._serialized_end=181
  _FACEDETECTED._serialized_start=183
  _FACEDETECTED._serialized_end=239
  _CAMERACAPTURE._serialized_start=241
  _CAMERACAPTURE._serialized_end=308
  _NUMERICREQUEST._serialized_start=310
  _NUMERICREQUEST._serialized_end=360
  _SOMERESPONSE._serialized_start=362
  _SOMERESPONSE._serialized_end=432
  _NAOCONTROLLER._serialized_start=435
  _NAOCONTROLLER._serialized_end=829
# @@protoc_insertion_point(module_scope)
