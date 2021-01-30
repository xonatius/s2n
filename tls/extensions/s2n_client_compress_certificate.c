/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

#include <sys/param.h>
#include <stdint.h>

#include "error/s2n_errno.h"
#include "stuffer/s2n_stuffer.h"
#include "tls/extensions/s2n_client_compress_certificate.h"
#include "tls/s2n_tls.h"
#include "tls/s2n_tls_parameters.h"

#include "utils/s2n_safety.h"

static bool s2n_client_compress_certificate_should_send(struct s2n_connection *conn);
static int s2n_client_compress_certificate_recv(struct s2n_connection *conn, struct s2n_stuffer *extension);

const s2n_extension_type s2n_client_compress_certificate_extension = {
    .iana_value = TLS_EXTENSION_COMPRESS_CERTIFICATE,
    .is_response = false,
    .send = s2n_extension_send_noop,
    .recv = s2n_client_compress_certificate_recv,
    .should_send = s2n_client_compress_certificate_should_send,
    .if_missing = s2n_extension_noop_if_missing,
};

static bool s2n_client_compress_certificate_should_send(struct s2n_connection *conn)
{
    return false;
}

static int s2n_client_compress_certificate_recv(struct s2n_connection *conn, struct s2n_stuffer *extension)
{
    notnull_check(conn);

    uint8_t length;
    GUARD(s2n_stuffer_read_uint8(extension, &length));

    S2N_ERROR_IF(length % 2 == 1, S2N_ERR_BAD_MESSAGE);
    S2N_ERROR_IF(s2n_stuffer_data_available(extension) != length, S2N_ERR_BAD_MESSAGE);

    for (uint8_t i = 0; i < length; i += 2) {
        uint16_t compression;
        GUARD(s2n_stuffer_read_uint16(extension, &compression));
        switch (compression) {
            case TLS_CERTIFICATE_COMPRESSION_ZLIB:
                conn->handshake.certificate_compression_zlib = 1;
                break;
            case TLS_CERTIFICATE_COMPRESSION_BROTLI:
                conn->handshake.certificate_compression_brotli = 1;
                break;
            case TLS_CERTIFICATE_COMPRESSION_ZSTD:
                conn->handshake.certificate_compression_zstd = 1;
                break;
            default:
                continue;
        }
    }

    return S2N_SUCCESS;
}
