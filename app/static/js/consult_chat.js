document.addEventListener('DOMContentLoaded', function () {
    const chatCard = document.querySelector('.chat-card');
    if (!chatCard) {
        return;
    }

    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const attachedFileLabel = document.getElementById('attachedFileLabel');
    const attachmentInput = document.getElementById('attachmentInput');
    const attachmentBtn = document.getElementById('attachmentBtn');
    const sendBtn = document.getElementById('chatSendBtn');
    const roomId = chatCard.getAttribute('data-room-id');
    const patientId = Number(chatCard.getAttribute('data-patient-id'));
    const doctorId = Number(chatCard.getAttribute('data-doctor-id'));
    const viewerId = Number(chatCard.getAttribute('data-viewer-id'));
    let editMessageId = null;

    function addMessage(text, role, attachmentUrl, messageId, senderId) {
        if (!text && attachmentUrl) {
            const ext = attachmentUrl.split('?')[0].split('.').pop().toLowerCase();
            if (['mp3', 'wav', 'ogg', 'm4a', 'webm'].includes(ext)) {
                text = 'Voice message';
            } else {
                text = '';
            }
        }

        if (attachmentUrl) {
            const existingAttachment = chatWindow.querySelector(`.msg-attachment a[href="${attachmentUrl}"], .msg-attachment audio source[src="${attachmentUrl}"]`);
            if (existingAttachment) {
                return;
            }
        }

        if (messageId) {
            const existing = chatWindow.querySelector(`.chat-msg[data-message-id="${messageId}"]`);
            if (existing) {
                return;
            }
        }

        const div = document.createElement('div');
        div.className = `chat-msg ${role}`;
        if (messageId) {
            div.setAttribute('data-message-id', messageId);
            if (senderId) {
                div.setAttribute('data-sender-id', senderId);
            }

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'msg-delete-btn';
            deleteBtn.setAttribute('data-message-id', messageId);
            deleteBtn.title = 'Delete message';
            deleteBtn.textContent = '✖';
            div.appendChild(deleteBtn);

            if (Number(senderId) === viewerId) {
                const editBtn = document.createElement('button');
                editBtn.className = 'msg-edit-btn';
                editBtn.setAttribute('data-message-id', messageId);
                editBtn.title = 'Edit message';
                editBtn.textContent = '✎';
                div.appendChild(editBtn);
            }
        }

        if (text) {
            const messageElement = document.createElement('div');
            messageElement.className = 'msg-text';
            messageElement.textContent = text;
            div.appendChild(messageElement);
        }

        if (attachmentUrl) {
            const attachmentEl = document.createElement('div');
            attachmentEl.className = 'msg-attachment';

            const normalizedUrl = attachmentUrl.split('?')[0].toLowerCase();
            const ext = normalizedUrl.split('.').pop().toLowerCase();
            const iconSpan = document.createElement('span');
            iconSpan.className = 'attachment-icon';
            iconSpan.textContent = '📎';
            attachmentEl.appendChild(iconSpan);

            if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
                const image = document.createElement('img');
                image.src = attachmentUrl;
                image.alt = 'Chat attachment';
                image.className = 'attachment-preview';
                const link = document.createElement('a');
                link.href = attachmentUrl;
                link.target = '_blank';
                link.appendChild(image);
                attachmentEl.appendChild(link);
            } else if (['mp3', 'wav', 'ogg', 'm4a', 'webm'].includes(ext) || attachmentUrl.includes('audio')) {
                const audio = document.createElement('audio');
                audio.controls = true;
                audio.className = 'attachment-audio';
                const source = document.createElement('source');
                source.src = attachmentUrl;
                if (ext === 'mp3') {
                    source.type = 'audio/mpeg';
                } else if (ext === 'webm') {
                    source.type = 'audio/webm';
                } else if (ext === 'ogg') {
                    source.type = 'audio/ogg';
                } else if (ext === 'm4a') {
                    source.type = 'audio/mp4';
                } else if (ext === 'wav') {
                    source.type = 'audio/wav';
                } else {
                    source.type = 'audio/*';
                }
                audio.appendChild(source);
                attachmentEl.appendChild(audio);
            } else {
                const link = document.createElement('a');
                link.href = attachmentUrl;
                link.target = '_blank';
                link.className = 'attachment-link';
                link.textContent = 'Download attachment';
                attachmentEl.appendChild(link);
            }

            div.appendChild(attachmentEl);
        }

        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    const socket = window.io();
    socket.emit('join_room', {
        room_id: roomId,
        patient_id: patientId,
        doctor_id: doctorId
    });

    const toastContainer = document.getElementById('toastContainer');
    const typingIndicator = document.getElementById('typingIndicator');

    function showToast(message, type='info') {
        if (!toastContainer) return;

        toastContainer.classList.remove('toast-container-hidden');
        toastContainer.classList.add('toast-container-visible');

        const toast = document.createElement('div');
        toast.className = `toast-item ${type}`;
        toast.textContent = message;

        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.remove();
            if (!toastContainer.querySelector('.toast-item')) {
                toastContainer.classList.remove('toast-container-visible');
                toastContainer.classList.add('toast-container-hidden');
            }
        }, 3200);
    }

    function sendPayload(attachmentUrl, text) {
        socket.emit('send_message', {
            room_id: roomId,
            patient_id: patientId,
            doctor_id: doctorId,
            message: (text || '').trim(),
            attachment_url: attachmentUrl || null
        });

        chatInput.value = '';
        attachedFileLabel.textContent = 'No file selected';
        attachmentInput.value = '';
    }

    attachmentBtn.addEventListener('click', function () {
        attachmentInput.click();
    });

    attachmentInput.addEventListener('change', function () {
        const file = attachmentInput.files[0];
        if (!file) {
            attachedFileLabel.textContent = 'No file selected';
            return;
        }

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            showToast('Only JPG/PNG/GIF/PDF files are allowed.', 'error');
            attachmentInput.value = '';
            attachedFileLabel.textContent = 'No file selected';
            return;
        }

        attachedFileLabel.textContent = `Uploading ${file.name} ...`;
        uploadAttachment(file)
            .then(function (attachmentUrl) {
                sendPayload(attachmentUrl, '');
                showToast('Attachment sent.', 'success');
            })
            .catch(function (error) {
                console.error('Attachment upload failed', error);
                showToast('Attachment upload failed.', 'error');
                attachedFileLabel.textContent = 'No file selected';
            });
    });

    socket.on('receive_message', function (payload) {
        console.log('receive_message payload', payload);
        if (!payload || payload.room_id && payload.room_id !== roomId) {
            return;
        }

        const role = Number(payload.sender_id) === viewerId ? 'user' : 'bot';
        addMessage(payload.message, role, payload.attachment_url, payload.id, payload.sender_id);
    });

    socket.on('message_deleted', function (payload) {
        if (!payload || !payload.message_id) {
            return;
        }
        const msg = chatWindow.querySelector(`.chat-msg[data-message-id="${payload.message_id}"]`);
        if (msg) {
            msg.remove();
        }
    });

    socket.on('message_edited', function (payload) {
        if (!payload || !payload.message_id) {
            return;
        }
        const msg = chatWindow.querySelector(`.chat-msg[data-message-id="${payload.message_id}"]`);
        if (msg) {
            const text = msg.querySelector('.msg-text');
            if (text) {
                text.textContent = payload.message;
            }
        }
    });

    socket.on('typing', function (payload) {
        if (!payload || payload.room_id !== roomId) {
            return;
        }
        if (payload.is_typing) {
            typingIndicator.textContent = `${payload.user_name || 'Participant'} is typing...`;
        } else {
            typingIndicator.textContent = '';
        }
    });

    // Presence updates are not displayed to keep chat UI clean and focused.
    // This can be re-enabled later if needed for live doctor availability.

    chatWindow.addEventListener('click', function (event) {
        const deleteBtn = event.target.closest('.msg-delete-btn');
        if (deleteBtn) {
            event.stopPropagation();
            const messageIdToDelete = deleteBtn.getAttribute('data-message-id');
            if (!messageIdToDelete) return;

            fetch(`/chat/message/${messageIdToDelete}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(function (resp) {
                if (!resp.ok) {
                    throw new Error('Delete request failed');
                }
                return resp.json();
            })
            .then(function (data) {
                if (!data.success) {
                    throw new Error(data.error || 'Delete not confirmed');
                }

                const msg = chatWindow.querySelector(`.chat-msg[data-message-id="${messageIdToDelete}"]`);
                if (msg) {
                    msg.remove();
                }

                socket.emit('delete_message', { room_id: roomId, message_id: messageIdToDelete });
                showToast('Message deleted', 'success');
            })
            .catch(function (error) {
                console.error('Delete action failed', error);
                showToast('Could not delete message', 'error');
            });

            return;
        }

        const editBtn = event.target.closest('.msg-edit-btn');
        if (editBtn) {
            event.stopPropagation();
            const messageIdToEdit = editBtn.getAttribute('data-message-id');
            if (!messageIdToEdit) return;

            const messageElement = chatWindow.querySelector(`.chat-msg[data-message-id="${messageIdToEdit}"] .msg-text`);
            if (!messageElement) return;

            chatInput.value = messageElement.textContent;
            editMessageId = messageIdToEdit;
            chatInput.focus();
            showToast('Edit mode enabled. Update your text and press Send.', 'info');
            return;
        }
    });

    function uploadAttachment(file) {
        const formData = new FormData();
        formData.append('attachment', file);

        return fetch('/chat/upload-attachment', {
            method: 'POST',
            body: formData
        }).then(function (resp) {
            if (!resp.ok) {
                throw new Error('Attachment upload failed');
            }
            return resp.json();
        }).then(function (data) {
            if (data.url) {
                return data.url;
            }
            throw new Error(data.error || 'Invalid response from upload');
        });
    }

    function encodeWAV(buffers, sampleRate) {
        const numChannels = 1;
        const interleaved = mergeBuffers(buffers, buffers.length * buffers[0].length);
        const buffer = new ArrayBuffer(44 + interleaved.length * 2);
        const view = new DataView(buffer);

        function writeString(view, offset, string) {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        }

        let offset = 0;
        writeString(view, offset, 'RIFF'); offset += 4;
        view.setUint32(offset, 36 + interleaved.length * 2, true); offset += 4;
        writeString(view, offset, 'WAVE'); offset += 4;
        writeString(view, offset, 'fmt '); offset += 4;
        view.setUint32(offset, 16, true); offset += 4;
        view.setUint16(offset, 1, true); offset += 2;
        view.setUint16(offset, numChannels, true); offset += 2;
        view.setUint32(offset, sampleRate, true); offset += 4;
        view.setUint32(offset, sampleRate * numChannels * 2, true); offset += 4;
        view.setUint16(offset, numChannels * 2, true); offset += 2;
        view.setUint16(offset, 16, true); offset += 2;
        writeString(view, offset, 'data'); offset += 4;
        view.setUint32(offset, interleaved.length * 2, true); offset += 4;

        let index = 0;
        for (let i = 0; i < interleaved.length; i++, index += 2) {
            const sample = Math.max(-1, Math.min(1, interleaved[i]));
            view.setInt16(44 + index, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        }

        return new Blob([view], { type: 'audio/wav' });
    }

    function mergeBuffers(buffers, totalLength) {
        const result = new Float32Array(totalLength);
        let offset = 0;
        for (let i = 0; i < buffers.length; i++) {
            result.set(buffers[i], offset);
            offset += buffers[i].length;
        }
        return result;
    }

    function sendMessage() {
        const message = chatInput.value.trim();

        if (!message) {
            return;
        }

        if (editMessageId) {
            fetch(`/chat/message/${editMessageId}/edit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            })
            .then(function (resp) {
                if (!resp.ok) throw new Error('Edit failed');
                return resp.json();
            })
            .then(function (data) {
                if (!data.success) throw new Error(data.error || 'Edit not confirmed');

                socket.emit('message_edited', {
                    room_id: roomId,
                    message_id: editMessageId,
                    message: message
                });

                const msg = chatWindow.querySelector(`.chat-msg[data-message-id="${editMessageId}"]`);
                if (msg) {
                    const text = msg.querySelector('.msg-text');
                    if (text) text.textContent = message;
                }

                showToast('Message edited successfully', 'success');
                editMessageId = null;
                chatInput.value = '';
            })
            .catch(function (err) {
                console.error('Edit failed', err);
                showToast('Could not edit message', 'error');
            });

            return;
        }

        sendPayload(null, message);
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    let typingTimeout = null;
    chatInput.addEventListener('input', function () {
        socket.emit('typing', { room_id: roomId, user_id: viewerId, user_name: sessionStorage.getItem('chat_user_name') || 'Someone', is_typing: true });
        if (typingTimeout) {
            clearTimeout(typingTimeout);
        }
        typingTimeout = setTimeout(function () {
            socket.emit('typing', { room_id: roomId, user_id: viewerId, user_name: sessionStorage.getItem('chat_user_name') || 'Someone', is_typing: false });
        }, 1200);
    });

    const darkModeToggle = document.getElementById('darkModeToggle');

    function applyDarkMode(enabled) {
        if (!chatCard) {
            console.error('Chat card not found for dark mode toggle');
            return;
        }

        if (enabled) {
            chatCard.classList.add('chat-dark-mode');
            chatCard.style.background = '#0f172a';
            chatCard.style.color = '#e2e8f0';
            const chatWindow = chatCard.querySelector('.chat-window');
            if (chatWindow) {
                chatWindow.style.background = '#111827';
                chatWindow.style.borderColor = '#334155';
            }
        } else {
            chatCard.classList.remove('chat-dark-mode');
            chatCard.style.background = '';
            chatCard.style.color = '';
            const chatWindow = chatCard.querySelector('.chat-window');
            if (chatWindow) {
                chatWindow.style.background = '';
                chatWindow.style.borderColor = '';
            }
        }

        if (darkModeToggle) {
            darkModeToggle.textContent = enabled ? '☀️ Light Mode' : '🌙 Dark Mode';
        }

        localStorage.setItem('ckd_dark_mode', enabled ? '1' : '0');
        console.log('set dark mode', enabled);
    }

    if (darkModeToggle) {
        const stored = localStorage.getItem('ckd_dark_mode');
        applyDarkMode(stored === '1');

        darkModeToggle.addEventListener('click', function () {
            const current = chatCard && chatCard.classList.contains('chat-dark-mode');
            applyDarkMode(!current);

            if (chatCard) {
                console.log('Dark mode toggled:', chatCard.classList.contains('chat-dark-mode')); 
            } else {
                console.error('Dark mode toggle: chatCard not found');
            }
        });
    }
});
