# Redis学习笔记—源码

## 字符串

Redis中的字符串是可以修改的字符串，在内存中它是以字节数组的形式存在的。Redis中的字符串叫SDS(Simple Dynamic String)，它的结构是一个带长度信息的字节数组。

```c
/*src/sds.h*/
struct __attribute__ ((__packed__)) sdshdr8 {
    uint8_t len; /* 实际使用的长度 */
    uint8_t alloc; /*分配长度，包含头部和null*/
    unsigned char flags; /* 3 标志位*/
    char buf[];
};
```

这样设计的目的：C语言中字符串的标准形式是以NULL结尾，获取字符串长度的函数为`strlen`，该函数的算法复杂度为$O(n)$。Redis为了对内存做极致的优化，不同长度的字符串采用不同的结构体表示。

对数组执行`append`操作时，如果数组没有冗余空间，则需要分配新数组，将旧数组的内容复制到新数组中，因此如果旧数组的长度很长时，内存分配与复制的开销会很大。

```c
/*src/sds.c*/
/* Append the specified binary-safe string pointed by 't' of 'len' bytes to the
 * end of the specified sds string 's'.
 *
 * After the call, the passed sds string is no longer valid and all the
 * references must be substituted with the new pointer returned by the call. */
sds sdscatlen(sds s, const void *t, size_t len) {
    size_t curlen = sdslen(s);/*原字符串长度*/

    s = sdsMakeRoomFor(s,len);/*按需调整空间*/
    if (s == NULL) return NULL;
    memcpy(s+curlen, t, len);/*追加字符串*/
    sdssetlen(s, curlen+len);/*设置追加后的长度*/
    s[curlen+len] = '\0';
    return s;
}
```

Redis规定字符串长度不能超过`512M`字节。

```c
/*src/t_string.c*/
static int checkStringLength(client *c, long long size) {
    if (size > 512*1024*1024) {
        addReplyError(c,"string exceeds maximum allowed size (512MB)");
        return C_ERR;
    }
    return C_OK;
}
```

### 扩容策略

字符串长度小于`1M`时，采用加倍策略扩容，当长度超过`1M`后，每次只多分配`1M`的冗余空间。

```c
/*src/sds.c*/
/* Enlarge the free space at the end of the sds string so that the caller
 * is sure that after calling this function can overwrite up to addlen
 * bytes after the end of the string, plus one more byte for nul term.
 *
 * Note: this does not change the *length* of the sds string as returned
 * by sdslen(), but only the free buffer space we have. */
sds sdsMakeRoomFor(sds s, size_t addlen) {
    void *sh, *newsh;
    //未分配数组长度
    size_t avail = sdsavail(s);
    size_t len, newlen;
    char type, oldtype = s[-1] & SDS_TYPE_MASK;
    int hdrlen;

    /* Return ASAP if there is enough space left. */
    if (avail >= addlen) return s;

    len = sdslen(s);
    sh = (char*)s-sdsHdrSize(oldtype);
    newlen = (len+addlen);
    // 如果新长度小于1M,则预分配为倍增
    if (newlen < SDS_MAX_PREALLOC)
        newlen *= 2;
    else
    // 如果新长度大于1M,则预分配+1M
        newlen += SDS_MAX_PREALLOC;

    type = sdsReqType(newlen);

    /* Don't use type 5: the user is appending to the string and type 5 is
     * not able to remember empty space, so sdsMakeRoomFor() must be called
     * at every appending operation. */
    if (type == SDS_TYPE_5) type = SDS_TYPE_8;

    hdrlen = sdsHdrSize(type);
    if (oldtype==type) {
        newsh = s_realloc(sh, hdrlen+newlen+1);
        if (newsh == NULL) return NULL;
        s = (char*)newsh+hdrlen;
    } else {
        /* Since the header size changes, need to move the string forward,
         * and can't use realloc */
        newsh = s_malloc(hdrlen+newlen+1);
        if (newsh == NULL) return NULL;
        memcpy((char*)newsh+hdrlen, s, len+1);
        s_free(sh);
        s = (char*)newsh+hdrlen;
        s[-1] = type;
        sdssetlen(s, len);
    }
    sdssetalloc(s, newlen);
    return s;
}
```

