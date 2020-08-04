// MIT License
//
// Copyright (c) 2020, The Regents of the University of California,
// through Lawrence Berkeley National Laboratory (subject to receipt of any
// required approvals from the U.S. Dept. of Energy).  All rights reserved.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

/**
 * \file timemory/settings/macros.hpp
 * \brief Include the macros for settings
 */

#pragma once

#include "timemory/compat/macros.h"
#include "timemory/dll.hpp"

//======================================================================================//
//
// Define macros for settings
//
//======================================================================================//
//
#if defined(TIMEMORY_SETTINGS_SOURCE)
//
#    define TIMEMORY_SETTINGS_LINKAGE(...) __VA_ARGS__
//
#elif defined(TIMEMORY_USE_EXTERN) || defined(TIMEMORY_USE_SETTINGS_EXTERN)
//
#    define TIMEMORY_SETTINGS_LINKAGE(...) __VA_ARGS__
//
#else
//
#    define TIMEMORY_SETTINGS_LINKAGE(...) inline __VA_ARGS__
//
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_DLL)
#    if defined(TIMEMORY_SETTINGS_SOURCE)
#        define TIMEMORY_SETTINGS_DLL tim_dll_export
#    elif defined(TIMEMORY_USE_EXTERN) || defined(TIMEMORY_USE_SETTINGS_EXTERN)
#        define TIMEMORY_SETTINGS_DLL tim_dll_import
#    else
#        define TIMEMORY_SETTINGS_DLL
#    endif
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_STATIC_ACCESSOR)
#    define TIMEMORY_STATIC_ACCESSOR(TYPE, FUNC, INIT)                                   \
    public:                                                                              \
        static TYPE& FUNC() TIMEMORY_VISIBILITY("default")                               \
        {                                                                                \
            return instance()->m__##FUNC;                                                \
        }                                                                                \
                                                                                         \
    private:                                                                             \
        TYPE m__##FUNC = INIT;
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_MEMBER_DECL)
#    define TIMEMORY_SETTINGS_MEMBER_DECL(TYPE, FUNC, ENV_VAR)                           \
    public:                                                                              \
        TYPE& get_##FUNC()                                                               \
        {                                                                                \
            return static_cast<tsettings<TYPE>*>(m_data[ENV_VAR].get())->get();          \
        }                                                                                \
                                                                                         \
        TYPE get_##FUNC() const                                                          \
        {                                                                                \
            auto ret = m_data.find(ENV_VAR);                                             \
            if(ret == m_data.end())                                                      \
                return TYPE{};                                                           \
            if(!ret->second)                                                             \
                return TYPE{};                                                           \
            return static_cast<tsettings<TYPE>*>(ret->second.get())->get();              \
        }                                                                                \
                                                                                         \
        static TYPE& FUNC() TIMEMORY_VISIBILITY("default")                               \
        {                                                                                \
            return instance()->get_##FUNC();                                             \
        }
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_REFERENCE_DECL)
#    define TIMEMORY_SETTINGS_REFERENCE_DECL(TYPE, FUNC, ENV_VAR)                        \
    public:                                                                              \
        TYPE& get_##FUNC()                                                               \
        {                                                                                \
            return static_cast<tsettings<TYPE, TYPE&>*>(m_data[ENV_VAR].get())->get();   \
        }                                                                                \
                                                                                         \
        TYPE get_##FUNC() const                                                          \
        {                                                                                \
            auto ret = m_data.find(ENV_VAR);                                             \
            if(ret == m_data.end())                                                      \
                return TYPE{};                                                           \
            if(!ret->second)                                                             \
                return TYPE{};                                                           \
            return static_cast<tsettings<TYPE, TYPE&>*>(ret->second.get())->get();       \
        }                                                                                \
                                                                                         \
        static TYPE& FUNC() TIMEMORY_VISIBILITY("default")                               \
        {                                                                                \
            return instance()->get_##FUNC();                                             \
        }
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_MEMBER_IMPL)
#    define TIMEMORY_SETTINGS_MEMBER_IMPL(TYPE, FUNC, ENV_VAR, DESC, INIT)               \
        m_data.insert(                                                                   \
            { ENV_VAR, std::make_shared<tsettings<TYPE>>(INIT, #FUNC, ENV_VAR, DESC) });
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_MEMBER_ARG_IMPL)
#    define TIMEMORY_SETTINGS_MEMBER_ARG_IMPL(TYPE, FUNC, ENV_VAR, DESC, INIT, ...)      \
        m_data.insert({ ENV_VAR, std::make_shared<tsettings<TYPE>>(                      \
                                     INIT, #FUNC, ENV_VAR, DESC, __VA_ARGS__) });
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_REFERENCE_IMPL)
#    define TIMEMORY_SETTINGS_REFERENCE_IMPL(TYPE, FUNC, ENV_VAR, DESC, INIT)            \
        m_data.insert({ ENV_VAR, std::make_shared<tsettings<TYPE, TYPE&>>(               \
                                     INIT, #FUNC, ENV_VAR, DESC) });
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_REFERENCE_ARG_IMPL)
#    define TIMEMORY_SETTINGS_REFERENCE_ARG_IMPL(TYPE, FUNC, ENV_VAR, DESC, INIT, ...)   \
        m_data.insert({ ENV_VAR, std::make_shared<tsettings<TYPE, TYPE&>>(               \
                                     INIT, #FUNC, ENV_VAR, DESC, __VA_ARGS__) });
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_ERROR_FUNCTION_MACRO)
#    if defined(__PRETTY_FUNCTION__)
#        define TIMEMORY_ERROR_FUNCTION_MACRO __PRETTY_FUNCTION__
#    else
#        define TIMEMORY_ERROR_FUNCTION_MACRO __FUNCTION__
#    endif
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_TRY_CATCH_NVP)
#    define TIMEMORY_SETTINGS_TRY_CATCH_NVP(ENV_VAR, FUNC)                               \
        try                                                                              \
        {                                                                                \
            ar(cereal::make_nvp(ENV_VAR, FUNC()));                                       \
        } catch(...)                                                                     \
        {}
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_CEREAL_REGISTER)
#    define TIMEMORY_SETTINGS_CEREAL_REGISTER(TYPE, LABEL)                               \
        TIMEMORY_SET_CLASS_VERSION(TIMEMORY_GET_CLASS_VERSION(::tim::vsettings), TYPE)   \
        namespace tim                                                                    \
        {                                                                                \
        namespace alias                                                                  \
        {                                                                                \
        using tsettings_##LABEL = tsettings<TYPE, TYPE>;                                 \
        }                                                                                \
        }                                                                                \
        CEREAL_REGISTER_TYPE(tim::alias::tsettings_##LABEL)                              \
        CEREAL_REGISTER_POLYMORPHIC_RELATION(::tim::vsettings,                           \
                                             tim::alias::tsettings_##LABEL)
#endif
//
//--------------------------------------------------------------------------------------//
//
#if !defined(TIMEMORY_SETTINGS_EXTERN_TEMPLATE)
//
#    if defined(TIMEMORY_SETTINGS_SOURCE)
//
#        define TIMEMORY_SETTINGS_EXTERN_TEMPLATE(API)                                   \
            namespace tim                                                                \
            {                                                                            \
            template std::shared_ptr<settings> settings::shared_instance<API>();         \
            template settings*                 settings::instance<API>();                \
            }
//
#    elif defined(TIMEMORY_USE_EXTERN) || defined(TIMEMORY_USE_SETTINGS_EXTERN)
//
#        define TIMEMORY_SETTINGS_EXTERN_TEMPLATE(API)                                   \
            namespace tim                                                                \
            {                                                                            \
            extern template std::shared_ptr<settings> settings::shared_instance<API>();  \
            extern template settings*                 settings::instance<API>();         \
            }
//
#    else
//
#        define TIMEMORY_SETTINGS_EXTERN_TEMPLATE(...)
//
#    endif
#endif
//
//======================================================================================//
//
