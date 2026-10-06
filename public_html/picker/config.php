<?php
// +---------------------------------------------------------------------------+
// | Media Gallery Plugin 1.6                                                  |
// +---------------------------------------------------------------------------+
// | $Id:: config.php 1994 2008-02-15 06:12:30Z mevans0263                    $|
// +---------------------------------------------------------------------------+
// | Copyright (C) 2005-2008 by the following authors:                         |
// |                                                                           |
// | Mark R. Evans               -    mark@gllabs.org                          |
// +---------------------------------------------------------------------------+
// |                                                                           |
// | This program is free software; you can redistribute it and/or             |
// | modify it under the terms of the GNU General Public License               |
// | as published by the Free Software Foundation; either version 2            |
// | of the License, or (at your option) any later version.                    |
// |                                                                           |
// | This program is distributed in the hope that it will be useful,           |
// | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
// | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             |
// | GNU General Public License for more details.                              |
// |                                                                           |
// | You should have received a copy of the GNU General Public License         |
// | along with this program; if not, write to the Free Software Foundation,   |
// | Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.           |
// |                                                                           |
// +---------------------------------------------------------------------------+
//


// Auto Tag defaults - sets default values for MG Media Browser
$_mgMB_CONF['at_border']          = isset($_MG_CONF['at_border']) ? (int) $_MG_CONF['at_border'] : 0;
$_mgMB_CONF['at_align']           = isset($_MG_CONF['at_align']) ? $_MG_CONF['at_align'] : 'none';
if ($_mgMB_CONF['at_align'] === 'auto') {
    $_mgMB_CONF['at_align'] = 'none';
}
$_mgMB_CONF['at_width']           = isset($_MG_CONF['at_width']) ? (int) $_MG_CONF['at_width'] : 0;
$_mgMB_CONF['at_height']          = isset($_MG_CONF['at_height']) ? (int) $_MG_CONF['at_height'] : 0;
$_mgMB_CONF['at_src']             = isset($_MG_CONF['at_src']) ? $_MG_CONF['at_src'] : 'tn';
$_mgMB_CONF['at_autoplay']        = isset($_MG_CONF['at_autoplay']) ? (int) $_MG_CONF['at_autoplay'] : 0;
$_mgMB_CONF['at_enable_link']     = isset($_MG_CONF['at_enable_link']) ? (int) $_MG_CONF['at_enable_link'] : 0;
$_mgMB_CONF['at_delay']           = isset($_MG_CONF['at_delay']) ? (int) $_MG_CONF['at_delay'] : 5;
$_mgMB_CONF['at_alturl']          = 0;          // Use alternate URL for link (if defined with the media item)
$_mgMB_CONF['enable_dest']        = 1;
?>
