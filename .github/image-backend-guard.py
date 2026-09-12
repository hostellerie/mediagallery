from pathlib import Path

p = Path('include/lib/imglib/lib-image.php')
text = p.read_text(encoding='utf-8')

anchor = """switch ( $_CONF['image_lib'] ) {
    case 'imagemagick' :    // ImageMagick...
        require_once $_CONF['path'] . 'plugins/mediagallery/include/lib/imglib/im_image.php';
        break;
    case 'netpbm' :    // NetPBM
        require_once $_CONF['path'] . 'plugins/mediagallery/include/lib/imglib/pbm_image.php';
        break;
    case 'gdlib' :    // GD Library
        require_once $_CONF['path'] . 'plugins/mediagallery/include/lib/imglib/gd_image.php';
        break;
    default:
        require_once $_CONF['path'] . 'plugins/mediagallery/include/lib/imglib/gd_image.php';
        break;
}
"""

helper = anchor + r'''
/**
 * Check that the image backend selected in Geeklog is actually usable.
 *
 * MediaGallery historically assumed the configured backend was available.
 * With GD selected but the PHP GD extension missing, image uploads could end
 * in an undefined-function fatal while non-image uploads continued to work.
 * Keep the check centralized here so uploads, conversions, rotations and
 * watermarks all fail cleanly for the same reason.
 *
 * @return array bool availability and human-readable error message
 */
function MG_getImageBackendStatus180()
{
    global $_CONF, $_MG_CONF;

    $backend = isset($_CONF['image_lib']) ? strtolower(trim($_CONF['image_lib'])) : 'gdlib';
    if ($backend === '') {
        $backend = 'gdlib';
    }

    if ($backend === 'gdlib') {
        $required = array(
            'imagecreatetruecolor',
            'imagecreatefromjpeg',
            'imagecreatefrompng',
            'imagecreatefromgif',
        );
        foreach ($required as $function) {
            if (!function_exists($function)) {
                return array(
                    false,
                    'MediaGallery image processing is unavailable: GD is selected but the PHP GD extension is not loaded. Install/enable GD or configure ImageMagick/NetPBM in Geeklog.'
                );
            }
        }
        return array(true, '');
    }

    if (!function_exists('exec')) {
        return array(
            false,
            'MediaGallery image processing is unavailable: the selected external image backend requires PHP exec(), but exec() is disabled.'
        );
    }

    if ($backend === 'imagemagick') {
        $prefix = isset($_MG_CONF['path_to_imagemagick']) ? $_MG_CONF['path_to_imagemagick'] : '';
        if (!MG_imageCommandAvailable180($prefix, 'identify') || !MG_imageCommandAvailable180($prefix, 'convert')) {
            return array(
                false,
                'MediaGallery image processing is unavailable: ImageMagick is selected but the identify/convert commands cannot be executed. Check the ImageMagick path in Geeklog.'
            );
        }
        return array(true, '');
    }

    if ($backend === 'netpbm') {
        $prefix = isset($_CONF['path_to_netpbm']) ? $_CONF['path_to_netpbm'] : '';
        $hasScaler = MG_imageCommandAvailable180($prefix, 'pamscale') || MG_imageCommandAvailable180($prefix, 'pnmscale');
        if (!$hasScaler || !MG_imageCommandAvailable180($prefix, 'jpegtopnm') || !MG_imageCommandAvailable180($prefix, 'pnmtojpeg')) {
            return array(
                false,
                'MediaGallery image processing is unavailable: NetPBM is selected but required NetPBM commands cannot be executed. Check the NetPBM path in Geeklog.'
            );
        }
        return array(true, '');
    }

    return array(
        false,
        'MediaGallery image processing is unavailable: Geeklog image_lib is set to an unsupported backend (' . $backend . ').'
    );
}

/**
 * Resolve an external image command either from an explicit configured path
 * or from the process PATH. This intentionally does not execute the command.
 */
function MG_imageCommandAvailable180($prefix, $binary)
{
    $suffix = (PHP_OS === 'WINNT') ? '.exe' : '';
    $binary .= $suffix;
    $prefix = trim((string) $prefix);

    if ($prefix !== '') {
        $path = rtrim($prefix, '/\\') . DIRECTORY_SEPARATOR . $binary;
        if (!is_file($path)) {
            return false;
        }
        return (PHP_OS === 'WINNT') ? true : is_executable($path);
    }

    $output = array();
    $status = 1;
    if (PHP_OS === 'WINNT') {
        @exec('where ' . escapeshellarg($binary), $output, $status);
    } else {
        @exec('command -v ' . escapeshellarg($binary), $output, $status);
    }
    return $status === 0 && !empty($output);
}

/**
 * Common guard used immediately before an operation requires image processing.
 */
function MG_requireImageBackend180()
{
    static $logged = false;

    list($available, $message) = MG_getImageBackendStatus180();
    if (!$available && !$logged) {
        COM_errorLog($message, 1);
        $logged = true;
    }
    return array($available, $message);
}
'''

if anchor not in text:
    raise SystemExit('backend include switch anchor not found')
text = text.replace(anchor, helper, 1)

def add_guard(signature, label):
    global text
    if signature not in text:
        raise SystemExit(label + ' signature not found')
    replacement = signature + "\n    list($backendAvailable, $backendMessage) = MG_requireImageBackend180();\n    if (!$backendAvailable) {\n        return array(false, $backendMessage);\n    }\n"
    text = text.replace(signature, replacement, 1)

add_guard("function MG_resizeImage($srcImage, $destImage, $dImageHeight, $dImageWidth, $mimeType='', $deleteSrc=0, $JpegQuality=85) {", 'resize')
add_guard("function MG_rotateImage($srcImage, $direction) {", 'rotate')
add_guard("function MG_convertImageFormat( $srcImage, $destImage, $destFormat, $deleteOriginal=1 ) {", 'convert')
add_guard("function MG_watermarkImage( $origImage, $watermarkImage, $opacity, $location ) {", 'watermark')

p.write_text(text, encoding='utf-8')

# Roadmap: mark backend detection complete and keep remaining RC validation explicit.
p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
roadmap = roadmap.replace(
    '- [ ] Detect and report clearly when no usable GD/ImageMagick/NetPBM backend is available.',
    '- [x] Detect and report clearly when the configured GD/ImageMagick/NetPBM backend is unavailable.'
)
if 'GD is selected but the PHP GD extension' not in roadmap:
    roadmap += "\n### Image backend validation\n\n- [x] Central backend guard covers resize, convert, rotate and watermark operations.\n- [x] GD selection now checks required PHP GD functions before image processing.\n- [x] ImageMagick and NetPBM selections validate configured binaries or commands available on PATH.\n- [x] Missing backend returns a clear MediaGallery error instead of an undefined-function fatal.\n- [ ] Validate the error message live once with GD intentionally disabled on the Geeklog 2.1.1/PHP 5.6 test instance.\n"
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
needle = "## Upload and import security\n\nImplemented:\n"
insert = """## Image backend validation\n\nImplemented:\n\n- centralized backend availability check in `include/lib/imglib/lib-image.php`;\n- GD requires the actual PHP GD functions before any resize/convert/rotate/watermark operation;\n- ImageMagick validates `identify` and `convert`;\n- NetPBM validates a scaler plus core JPEG conversion commands;\n- explicit-path configurations are checked directly while empty paths may resolve commands through `PATH`;\n- missing/unusable backends now return a readable MediaGallery error and log it once per request instead of reaching undefined image functions.\n\nThe Geeklog 2.1.1 / PHP 5.6 live test confirmed that image upload succeeds after enabling GD, while PDF/ZIP uploads did not require the image backend.\n\n"""
if needle not in notes:
    raise SystemExit('implementation notes anchor not found')
notes = notes.replace(needle, insert + needle, 1)
p.write_text(notes, encoding='utf-8')

print('Image backend guard patch prepared.')
