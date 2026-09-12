<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | MediaGallery 1.8.0 input compatibility                                   |
// +--------------------------------------------------------------------------+

namespace Geeklog;

/*
 * Geeklog 2.1.1 exposes the native GL_Input objects as $_INPUT and $_FINPUT.
 * Geeklog 2.2.x exposes the static Geeklog\Input API used by MediaGallery.
 *
 * Define only the missing 2.2-style facade and delegate every operation to
 * Geeklog 2.1.1's native input objects.  No filtering logic is duplicated.
 */
if (!class_exists(__NAMESPACE__ . '\\Input', false)) {
    class Input
    {
        private static function rawInput()
        {
            global $_INPUT;
            return $_INPUT;
        }

        private static function filteredInput()
        {
            global $_FINPUT;
            return $_FINPUT;
        }

        public static function get($name, $defaultValue = null)
        {
            return self::rawInput()->get($name, $defaultValue);
        }

        public static function post($name, $defaultValue = null)
        {
            return self::rawInput()->post($name, $defaultValue);
        }

        public static function cookie($name, $defaultValue = null)
        {
            return self::rawInput()->cookie($name, $defaultValue);
        }

        public static function server($name, $defaultValue = null)
        {
            return self::rawInput()->server($name, $defaultValue);
        }

        public static function files($name, $defaultValue = null)
        {
            return self::rawInput()->files($name, $defaultValue);
        }

        public static function env($name, $defaultValue = null)
        {
            return self::rawInput()->env($name, $defaultValue);
        }

        public static function request($name, $defaultValue = null)
        {
            return self::rawInput()->request($name, $defaultValue);
        }

        public static function session($name, $defaultValue = null)
        {
            return self::rawInput()->session($name, $defaultValue);
        }

        public static function req($name, $defaultValue = null)
        {
            return self::rawInput()->req($name, $defaultValue);
        }

        public static function getOrPost($name, $defaultValue = null)
        {
            $value = self::get($name, null);
            return ($value === null) ? self::post($name, $defaultValue) : $value;
        }

        public static function postOrGet($name, $defaultValue = null)
        {
            $value = self::post($name, null);
            return ($value === null) ? self::get($name, $defaultValue) : $value;
        }

        public static function fGet($name, $defaultValue = null)
        {
            return self::filteredInput()->get($name, $defaultValue);
        }

        public static function fPost($name, $defaultValue = null)
        {
            return self::filteredInput()->post($name, $defaultValue);
        }

        public static function fCookie($name, $defaultValue = null)
        {
            return self::filteredInput()->cookie($name, $defaultValue);
        }

        public static function fServer($name, $defaultValue = null)
        {
            return self::filteredInput()->server($name, $defaultValue);
        }

        public static function fFiles($name, $defaultValue = null)
        {
            return self::filteredInput()->files($name, $defaultValue);
        }

        public static function fEnv($name, $defaultValue = null)
        {
            return self::filteredInput()->env($name, $defaultValue);
        }

        public static function fRequest($name, $defaultValue = null)
        {
            return self::filteredInput()->request($name, $defaultValue);
        }

        public static function fSession($name, $defaultValue = null)
        {
            return self::filteredInput()->session($name, $defaultValue);
        }

        public static function fReq($name, $defaultValue = null)
        {
            return self::filteredInput()->req($name, $defaultValue);
        }

        public static function fGetOrPost($name, $defaultValue = null)
        {
            $value = self::fGet($name, null);
            return ($value === null) ? self::fPost($name, $defaultValue) : $value;
        }

        public static function fPostOrGet($name, $defaultValue = null)
        {
            $value = self::fPost($name, null);
            return ($value === null) ? self::fGet($name, $defaultValue) : $value;
        }
    }
}
