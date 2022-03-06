#ifndef CORE_HPP
#define CORE_HPP

#define VM_VERSION "0.0.1"

typedef int pc_t;

#define PUBLIC
#define STATIC

/*
 * Operating System Evaluation
 */
 // Windows
#if (defined(_WIN32) || defined(_WIN64))
  #define NP_OS_WINDOWS 1
#else
  #define NP_OS_WINDOWS 0
#endif
// linux
#if (defined(__linux) || defined(__linux__))
  #define NP_OS_LINUX 1
#else
  #define NP_OS_LINUX 0
#endif
// Apple
#if defined(__APPLE__)
  #define NP_OS_APPLE 1
#else
  #define NP_OS_APPLE 0
#endif
// FreeBSD
#if (defined(__FreeBSD__) || defined(__FreeBSD_kernel__))
  #define NP_OS_FREEBSD 1
#else
  #define NP_OS_FREEBSD 0
#endif
// Sun solaris
#if (defined(__sun))
  #define NP_OS_SOLARIS 1
#else
  #define NP_OS_SOLARIS 0
#endif
// Android
#if (defined(__ANDROID__))
  #define NP_OS_ANDROID 1
#else
  #define NP_OS_ANDROID 0
#endif

/*
 * Compiler Evaluation
 */
// g++ gcc
#if (defined(__GNUC__))
  #define NP_COMPILER_GCC 1
#else
  #define NP_COMPILER_GCC 0
#endif
// VC++
#if defined(_MSC_VER)
  #define NP_COMPILER_MSVC 1
#else
  #define NP_COMPILER_MSVC 0
#endif
// Clang
#if (defined(__clang__) && (__clang__ == 1))
  #define NP_COMPILER_CLANG 1
#else
  #define NP_COMPILER_CLANG 0
#endif

/*
 * no exception definations of different cpp version.
 */
#if __cplusplus < 201103L
    #define NOEXCEPT throw()
#else
    #define NOEXCEPT noexcept
#endif

/*
 * A macron of disable copy constructor and operator=.
 * My inspiration from Apache Caffe source code.
 */
#define DISABLE_COPY(_Ty) \
    private:  \
      _Ty(const _Ty&); \
      _Ty& operator=(const _Ty&);



#define __PTR_IN__ 
#define __PTR_OUT__
#define __PTR_INNER__


#ifdef __GNUC__
#define DEPRECATED(func) func __attribute__ ((deprecated))
#elif defined(_MSC_VER)
#define DEPRECATED(func) __declspec(deprecated) func
#else
#pragma message("WARNING: You need to implement DEPRECATED for this compiler")
#define DEPRECATED(func) func
#endif

#endif // endif CORE_HPP