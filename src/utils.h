#ifndef NATIVE_MEMORY_AGENT_UTILS_H
#define NATIVE_MEMORY_AGENT_UTILS_H

#include "types.h"
#include <string>
#include <jvmti.h>


const char *get_reference_type_description(jvmtiHeapReferenceKind kind);

std::string get_tag_description(Tag *tag);

jobjectArray toJavaArray(JNIEnv *env, jobject *objects, jint count);

jobjectArray toJavaArray(JNIEnv *env, std::vector<std::vector<jint>> &prev);

jobjectArray wrapWithArray(JNIEnv *env, jobjectArray first, jobjectArray second);

GcTag *createGcTag();

jlong gcTagToPointer(GcTag *tag);

GcTag *pointerToGcTag(jlong tag_ptr);

#endif //NATIVE_MEMORY_AGENT_UTILS_H
