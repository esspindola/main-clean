// ----------------------------------------------------------------------------------
// Parte 1: Imports de Módulos Necesarios
// ----------------------------------------------------------------------------------
import Debug "mo:base/Debug";              
import Time "mo:base/Time";                
import HashMap "mo:base/HashMap";          
import Text "mo:base/Text";                
import Int "mo:base/Int";                  
import Iter "mo:base/Iter";                // Para iteradores
import Nat32 "mo:base/Nat32";            // Para conversión de tipos

// Importar el IC management canister para Bitcoin (si tienes acceso)
// import IC "mo:ic/IC";

// ----------------------------------------------------------------------------------
// Parte 2: Actor Principal con Tipos y Funciones
// ----------------------------------------------------------------------------------
persistent actor PaymentManager {

    // ----------------------------------------------------------------------------------
    // Definición del Tipo de Dato 'PaymentRecord'
    // ----------------------------------------------------------------------------------
    type PaymentRecord = {
        ventaId : Text;           // Identificador único para la venta.
        bitcoinAddress : Text;    // La dirección BTC generada para esta venta.
        expectedAmountSatoshi : Nat64; // El monto de BTC esperado (en Satoshi).
        receivedAmountSatoshi : Nat64; // El monto de BTC que se ha recibido hasta ahora (en Satoshi).
        status : Text;            // El estado actual del pago ("PENDING", "RECEIVED_PARTIAL", "CONFIRMED", "ERROR").
        createdAt : Int;          // Marca de tiempo de cuándo se creó el registro.
        updatedAt : Int;          // Marca de tiempo de la última actualización del registro.
    };
    // ----------------------------------------------------------------------------------
    // Almacenamiento Persistente de los Registros de Pago
    // ----------------------------------------------------------------------------------
    private transient var paymentRecords = HashMap.HashMap<Text, PaymentRecord>(10, Text.equal, Text.hash);

    // Para persistencia, usamos pre/post upgrade hooks
    private var paymentRecordsEntries : [(Text, PaymentRecord)] = [];

    // Restaurar datos después de upgrade
    system func preupgrade() {
        paymentRecordsEntries := Iter.toArray(paymentRecords.entries());
    };

    system func postupgrade() {
        paymentRecords := HashMap.fromIter<Text, PaymentRecord>(
            paymentRecordsEntries.vals(), 
            paymentRecordsEntries.size(), 
            Text.equal, 
            Text.hash
        );
        paymentRecordsEntries := [];
    };

    // ----------------------------------------------------------------------------------
    // Parte 4: Funciones Públicas del Canister
    // ----------------------------------------------------------------------------------

    // =================================================================================
    // FUNCIONES MOCK PARA PRUEBAS (Simulan comportamiento real de Bitcoin)
    // =================================================================================
    
    // Simula diferentes tipos de direcciones Bitcoin reales
    private func generateMockBitcoinAddress() : Text {
        let seed = Int.abs(Time.now());
        let addressType = seed % 3;
        
        switch (addressType) {
            case (0) {
                // Dirección P2PKH (Legacy) - empieza con '1'
                "1" # generateRandomString(33);
            };
            case (1) {
                // Dirección P2SH (Script) - empieza con '3'  
                "3" # generateRandomString(33);
            };
            case (_) {
                // Dirección Bech32 (SegWit) - empieza con 'bc1q'
                "bc1q" # generateRandomString(39);
            };
        };
    };
    
    // Genera strings aleatorios para direcciones realistas
    private func generateRandomString(length: Nat) : Text {
        let _chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        let seed = Int.abs(Time.now());
        var result = "";
        var i = 0;
        var currentSeed = seed;
        
        while (i < length) {
            currentSeed := (currentSeed * 1103515245 + 12345) % 2147483647;
            let charIndex = Int.abs(currentSeed) % 62;
            // Simulamos obtener el carácter (en un entorno real usarías Text.get)
            result := result # Int.toText(charIndex % 10);
            i += 1;
        };
        result;
    };

    // Simula el comportamiento real de consulta de balance Bitcoin
    private func getMockBalance(address : Text) : async Nat64 {
        let addressHash = Text.hash(address);
        let baseBalance = Nat32.toNat64(addressHash % 1000000); // 0-999,999 satoshis
        
        // Simula diferentes escenarios realistas
        let scenario = addressHash % 10;
        
        switch (scenario) {
            case (0) { 0; };
            case (1) { 0; };
            case (2) { 0; };
            case (3) {
                // 20% - Balance pequeño (menos de 0.001 BTC = 100,000 satoshis)
                baseBalance % 100000;
            };
            case (4) {
                // Balance pequeño continuación
                baseBalance % 100000;
            };
            case (5) {
                // 20% - Balance medio (0.001 - 0.01 BTC = 100,000 - 1,000,000 satoshis)
                100000 + (baseBalance % 900000);
            };
            case (6) {
                // Balance medio continuación
                100000 + (baseBalance % 900000);
            };
            case (7) {
                // 10% - Balance alto (0.01 - 0.1 BTC = 1,000,000 - 10,000,000 satoshis)
                1000000 + (baseBalance % 9000000);
            };
            case (_) {
                // 20% - Balance muy alto (0.1+ BTC = 10,000,000+ satoshis)
                10000000 + (baseBalance % 90000000);
            };
        };
    };
    
    // Simula el tiempo de confirmación de la red Bitcoin
    private func simulateNetworkDelay() : async () {
        // En un entorno real, aquí habría una pausa real
        // Por ahora solo agregamos logs que simulan el proceso
        Debug.print("🔍 Consultando mempool de Bitcoin...");
        Debug.print("⛏️  Esperando confirmaciones de la red...");
        Debug.print("✅ Información de blockchain actualizada");
    };

    // 1. generateBitcoinAddress
    public func generateBitcoinAddress(ventaId : Text, expectedAmountSatoshi : Nat64) : async Text {
        // Verificar si ya existe
        switch (paymentRecords.get(ventaId)) {
            case (?_) {
                Debug.print("Venta ID ya existe: " # ventaId);
                return "Error: Venta ID ya existe. Use un ID único.";
            };
            case null { /* continuar */ };
        };

        // Generar dirección Bitcoin realista
        let address = generateMockBitcoinAddress();
        Debug.print("🏦 Generando nueva dirección Bitcoin...");
        Debug.print("📍 Dirección generada: " # address);
        
        // En producción sería:
        // let addressResult = await BitcoinCanister.get_p2pkh_address({...});

        let currentTime = Time.now();
        let newRecord : PaymentRecord = {
            ventaId = ventaId;
            bitcoinAddress = address;
            expectedAmountSatoshi = expectedAmountSatoshi;
            receivedAmountSatoshi = 0;
            status = "PENDING";
            createdAt = currentTime;
            updatedAt = currentTime;
        };

        paymentRecords.put(ventaId, newRecord);

        Debug.print("Dirección BTC generada para venta " # ventaId # ": " # address);
        return address;
    };

    // 2. getPaymentStatus
    public func getPaymentStatus(ventaId : Text) : async {status: Text; amount: Nat64; message: Text} {
        switch (paymentRecords.get(ventaId)) {
            case null {
                Debug.print("Venta ID no encontrada: " # ventaId);
                return {
                    status = "NOT_FOUND";
                    amount = 0;
                    message = "No se encontró registro para el ID de venta.";
                };
            };
            case (?record) {
                // Si ya está confirmado, devolver el estado actual
                if (record.status == "CONFIRMED") {
                    return {
                        status = record.status;
                        amount = record.receivedAmountSatoshi;
                        message = "Pago ya confirmado y verificado.";
                    };
                };

                // Simular consulta real a la blockchain
                await simulateNetworkDelay();
                let currentBalanceSatoshi = await getMockBalance(record.bitcoinAddress);
                
                Debug.print("⚡ Consultando blockchain Bitcoin...");
                Debug.print("📊 Balance encontrado: " # debug_show(currentBalanceSatoshi) # " satoshis");
                Debug.print("🎯 Balance esperado: " # debug_show(record.expectedAmountSatoshi) # " satoshis");
                
                // En producción sería:
                // let balanceResult = await BitcoinCanister.get_balance({...});

                Debug.print("Balance actual para " # record.bitcoinAddress # ": " # debug_show(currentBalanceSatoshi) # " satoshis");

                // Determinar el nuevo estado basado en el balance
                let newStatus = if (currentBalanceSatoshi >= record.expectedAmountSatoshi) {
                    Debug.print("✅ ¡Pago confirmado para venta " # ventaId # "!");
                    Debug.print("💰 Monto recibido: " # debug_show(currentBalanceSatoshi) # " satoshis");
                    "CONFIRMED";
                } else if (currentBalanceSatoshi > 0) {
                    Debug.print("⚠️  Pago parcial para venta " # ventaId);
                    Debug.print("💸 Faltan: " # debug_show(record.expectedAmountSatoshi - currentBalanceSatoshi) # " satoshis");
                    "RECEIVED_PARTIAL";
                } else {
                    Debug.print("⏳ Esperando pago para venta " # ventaId);
                    "PENDING";
                };

                // Crear record actualizado
                let updatedRecord : PaymentRecord = {
                    ventaId = record.ventaId;
                    bitcoinAddress = record.bitcoinAddress;
                    expectedAmountSatoshi = record.expectedAmountSatoshi;
                    receivedAmountSatoshi = currentBalanceSatoshi;
                    status = newStatus;
                    createdAt = record.createdAt;
                    updatedAt = Time.now();
                };

                // Actualizar el registro
                paymentRecords.put(ventaId, updatedRecord);

                return {
                    status = updatedRecord.status;
                    amount = updatedRecord.receivedAmountSatoshi;
                    message = "Estado del pago actualizado.";
                };
            };
        };
    };

    // 3. getPaymentRecords (Útil para depuración)
    public query func getPaymentRecords() : async [PaymentRecord] {
        Iter.toArray(paymentRecords.vals());
    };

    // 4. getPaymentRecord - obtener un registro específico
    public query func getPaymentRecord(ventaId : Text) : async ?PaymentRecord {
        switch (paymentRecords.get(ventaId)) {
            case (?record) { ?record };
            case null { null };
        };
    };

    // 5. deletePaymentRecord (¡Solo para pruebas o admin!)
    public func deletePaymentRecord(ventaId : Text) : async Text {
        switch (paymentRecords.get(ventaId)) {
            case (?_) {
                paymentRecords.delete(ventaId);
                Debug.print("Registro borrado exitosamente para venta ID: " # ventaId);
                "Registro borrado exitosamente.";
            };
            case null {
                Debug.print("Venta ID no encontrada para borrar: " # ventaId);
                "Venta ID no encontrada.";
            };
        };
    };

    // =================================================================================
    // FUNCIONES ADICIONALES PARA TESTING Y DEMOSTRACIÓN
    // =================================================================================
    
    // Función para simular un pago llegando a una dirección
    public func simulatePayment(ventaId : Text, amountSatoshi : Nat64) : async Text {
        switch (paymentRecords.get(ventaId)) {
            case null {
                "❌ Error: Venta ID no encontrada: " # ventaId;
            };
            case (?record) {
                Debug.print("💳 Simulando pago entrante...");
                Debug.print("📍 Dirección: " # record.bitcoinAddress);
                Debug.print("💰 Monto: " # debug_show(amountSatoshi) # " satoshis");
                
                // Actualizar el balance simulado modificando el hash base
                // (En un entorno real, esto vendría de la blockchain)
                let updatedRecord : PaymentRecord = {
                    ventaId = record.ventaId;
                    bitcoinAddress = record.bitcoinAddress;
                    expectedAmountSatoshi = record.expectedAmountSatoshi;
                    receivedAmountSatoshi = amountSatoshi;
                    status = if (amountSatoshi >= record.expectedAmountSatoshi) {
                        "CONFIRMED";
                    } else if (amountSatoshi > 0) {
                        "RECEIVED_PARTIAL";
                    } else {
                        "PENDING";
                    };
                    createdAt = record.createdAt;
                    updatedAt = Time.now();
                };
                
                paymentRecords.put(ventaId, updatedRecord);
                "✅ Pago simulado exitosamente. Estado: " # updatedRecord.status;
            };
        };
    };
    
    // Función para obtener estadísticas del sistema
    public query func getSystemStats() : async {
        totalRecords: Nat;
        pendingPayments: Nat;
        confirmedPayments: Nat;
        partialPayments: Nat;
    } {
        var pending = 0;
        var confirmed = 0;
        var partial = 0;
        
        for (record in paymentRecords.vals()) {
            if (record.status == "PENDING") {
                pending := pending + 1;
            } else if (record.status == "CONFIRMED") {
                confirmed := confirmed + 1;
            } else if (record.status == "RECEIVED_PARTIAL") {
                partial := partial + 1;
            };
        };
        
        {
            totalRecords = paymentRecords.size();
            pendingPayments = pending;
            confirmedPayments = confirmed;
            partialPayments = partial;
        };
    };
}