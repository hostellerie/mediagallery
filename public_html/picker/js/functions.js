/* MediaGallery simple reusable picker with persistent multi-selection. */
(function (window, document) {
    'use strict';

    var form;
    var storageKey;
    var selected = [];

    function readSelection() {
        var raw;
        var ids;
        var i;

        selected = [];
        try {
            raw = window.sessionStorage.getItem(storageKey);
            ids = raw ? JSON.parse(raw) : [];
        } catch (e) {
            ids = [];
        }

        if (!Array.isArray(ids)) {
            ids = [];
        }

        for (i = 0; i < ids.length; i += 1) {
            if (/^[0-9]+$/.test(String(ids[i]))
                && selected.indexOf(String(ids[i])) === -1
            ) {
                selected.push(String(ids[i]));
            }
        }
    }

    function writeSelection() {
        try {
            window.sessionStorage.setItem(storageKey, JSON.stringify(selected));
        } catch (e) {
            // The picker still works on the current page if storage is unavailable.
        }
    }

    function clearSelectionStore() {
        selected = [];
        try {
            window.sessionStorage.removeItem(storageKey);
        } catch (e) {
            // Ignore storage failures.
        }
    }

    function selectedIds() {
        return selected.slice();
    }

    function isSelected(id) {
        return selected.indexOf(String(id)) !== -1;
    }

    function addSelected(id) {
        id = String(id);
        if (!isSelected(id)) {
            selected.push(id);
        }
    }

    function removeSelected(id) {
        var index = selected.indexOf(String(id));
        if (index !== -1) {
            selected.splice(index, 1);
        }
    }

    function setCardState(input, isSelected) {
        var card = input.closest ? input.closest('.cell') : input.parentNode;
        input.checked = isSelected;
        if (card && card.classList) {
            if (isSelected) {
                card.classList.add('is-selected');
            } else {
                card.classList.remove('is-selected');
            }
        }
    }

    function syncVisibleSelection() {
        var inputs = document.querySelectorAll('input[name="thumbnail"]');
        var i;
        var id;

        for (i = 0; i < inputs.length; i += 1) {
            id = String(inputs[i].value);
            setCardState(inputs[i], isSelected(id));
        }
    }

    function updateStatus() {
        var ids = selectedIds();
        var count = ids.length;
        var countNode = document.getElementById('mg-picker-selected-count');
        var labelNode = document.getElementById('mg-picker-selected-label');
        var insertButton = document.getElementById('mg-picker-insert');
        var clearButton = document.getElementById('mg-picker-clear');
        var plural = form.getAttribute('data-selected-plural');
        var singular = form.getAttribute('data-selected-singular');
        var insertOne = form.getAttribute('data-insert-one');
        var insertMany = form.getAttribute('data-insert-many');

        if (countNode) {
            countNode.textContent = String(count);
        }
        if (labelNode) {
            labelNode.textContent = count === 1 ? singular : plural;
        }
        if (insertButton) {
            insertButton.disabled = count === 0;
            insertButton.textContent = count === 1
                ? insertOne
                : insertMany.replace('%d', String(count));
        }
        if (clearButton) {
            clearButton.disabled = count === 0;
        }
    }

    function albumId(formElement) {
        var source = formElement.current_album_id
            ? formElement.current_album_id.value
            : formElement.aid.value;
        var value = parseInt(source, 10);

        return isFinite(value) && value > 0 ? value : 0;
    }

    function insertAutotag(tag) {
        if (typeof window.InsertHtml === 'function') {
            window.InsertHtml(tag);
            clearSelectionStore();
            window.close();
        }
        return false;
    }

    window.insertImages = function () {
        var ids = selectedIds();
        var tags = [];
        var i;

        if (!ids.length) {
            window.alert(lang.no_media);
            return false;
        }

        for (i = 0; i < ids.length; i += 1) {
            tags.push('[media:' + ids[i] + ' width:640 src:disp align:none link:1]');
        }

        return insertAutotag(tags.join('\n\n'));
    };

    window.insertAlbum = function (formElement) {
        var id = albumId(formElement);

        if (!id) {
            window.alert(lang.no_album);
            return false;
        }

        return insertAutotag('[album:' + id + ' width:640 align:none link:1]');
    };

    function initialize() {
        form = document.forms.mediabrowser;
        if (!form) {
            return;
        }

        storageKey = 'mediagallery-picker:' + (form.getAttribute('data-selection-key') || 'default');
        readSelection();
        syncVisibleSelection();
        updateStatus();

        document.addEventListener('change', function (event) {
            var input = event.target;
            var id;

            if (!input || input.name !== 'thumbnail') {
                return;
            }

            id = String(input.value);
            if (input.checked) {
                addSelected(id);
            } else {
                removeSelected(id);
            }

            setCardState(input, input.checked);
            writeSelection();
            updateStatus();
        });

        var clearButton = document.getElementById('mg-picker-clear');
        if (clearButton) {
            clearButton.addEventListener('click', function () {
                clearSelectionStore();
                syncVisibleSelection();
                updateStatus();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
}(window, document));
