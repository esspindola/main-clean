import React, { useState, useEffect } from 'react';
import { ZatoBoxPayments_backend } from 'declarations/ZatoBoxPayments_backend';
import './index.scss';

const App = () => {
  // Estados principales
  const [loading, setLoading] = useState(false);
  const [payments, setPayments] = useState([]);
  const [stats, setStats] = useState({
    totalRecords: 0,
    pendingPayments: 0,
    confirmedPayments: 0,
    partialPayments: 0
  });

  // Estados de modales
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showSimulateModal, setShowSimulateModal] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState(null);

  // Estados de formularios
  const [newPayment, setNewPayment] = useState({
    ventaId: '',
    expectedAmount: ''
  });
  const [simulateAmount, setSimulateAmount] = useState('');

  // Estados de notificaciones
  const [alert, setAlert] = useState({ show: false, type: '', message: '' });

  // Cargar datos al iniciar
  useEffect(() => {
    loadPayments();
    loadStats();
  }, []);

  // Función para mostrar alertas
  const showAlert = (type, message) => {
    setAlert({ show: true, type, message });
    setTimeout(() => setAlert({ show: false, type: '', message: '' }), 5000);
  };

  // Cargar lista de pagos
  const loadPayments = async () => {
    try {
      setLoading(true);
      const result = await ZatoBoxPayments_backend.getPaymentRecords();
      setPayments(result);
    } catch (error) {
      showAlert('error', 'Error al cargar los pagos: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Cargar estadísticas
  const loadStats = async () => {
  try {
    const result = await ZatoBoxPayments_backend.getSystemStats();
    console.log("Resultado crudo:", result);

    // Si result es un array de arrays, conviértelo a objeto:
    const statsObject = Object.fromEntries(result);

    // Convierte BigInt a Number si es necesario:
    setStats({
      totalRecords: Number(statsObject.totalRecords || 0),
      pendingPayments: Number(statsObject.pendingPayments || 0),
      confirmedPayments: Number(statsObject.confirmedPayments || 0),
      partialPayments: Number(statsObject.partialPayments || 0),
    });
  } catch (error) {
    console.error('Error al cargar estadísticas:', error);
  }
};



  // Crear nueva dirección de pago
  const createPayment = async () => {
    if (!newPayment.ventaId || !newPayment.expectedAmount) {
      showAlert('error', 'Por favor completa todos los campos');
      return;
    }

    try {
      setLoading(true);
      const expectedAmountSatoshi = BigInt(Math.floor(parseFloat(newPayment.expectedAmount) * 100000000));
      const address = await ZatoBoxPayments_backend.generateBitcoinAddress(
        newPayment.ventaId,
        expectedAmountSatoshi
      );

      if (address.startsWith('Error:')) {
        showAlert('error', address);
      } else {
        showAlert('success', `¡Dirección Bitcoin generada exitosamente! ${address}`);
        setNewPayment({ ventaId: '', expectedAmount: '' });
        setShowCreateModal(false);
        loadPayments();
        loadStats();
      }
    } catch (error) {
      showAlert('error', 'Error al generar dirección: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Verificar estado de pago
  const checkPaymentStatus = async (ventaId) => {
    try {
      setLoading(true);
      const result = await ZatoBoxPayments_backend.getPaymentStatus(ventaId);
      
      if (result.status === 'NOT_FOUND') {
        showAlert('error', result.message);
      } else {
        showAlert('info', `Estado: ${result.status} - ${result.message}`);
        loadPayments();
        loadStats();
      }
    } catch (error) {
      showAlert('error', 'Error al verificar estado: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Simular pago
  const simulatePayment = async () => {
    if (!simulateAmount || !selectedPayment) {
      showAlert('error', 'Por favor ingresa un monto válido');
      return;
    }

    try {
      setLoading(true);
      const amountSatoshi = BigInt(Math.floor(parseFloat(simulateAmount) * 100000000));
      const result = await ZatoBoxPayments_backend.simulatePayment(
        selectedPayment.ventaId,
        amountSatoshi
      );
      
      showAlert('success', result);
      setSimulateAmount('');
      setShowSimulateModal(false);
      loadPayments();
      loadStats();
    } catch (error) {
      showAlert('error', 'Error al simular pago: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Eliminar pago
  const deletePayment = async (ventaId) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este pago?')) {
      return;
    }

    try {
      setLoading(true);
      const result = await ZatoBoxPayments_backend.deletePaymentRecord(ventaId);
      showAlert('success', result);
      loadPayments();
      loadStats();
    } catch (error) {
      showAlert('error', 'Error al eliminar pago: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Formatear satoshis a BTC
  const formatBTC = (satoshis) => {
    return (Number(satoshis) / 100000000).toFixed(8);
  };

  // Obtener clase CSS para el estado
  const getStatusClass = (status) => {
    switch (status) {
      case 'CONFIRMED': return 'status-confirmed';
      case 'RECEIVED_PARTIAL': return 'status-partial';
      case 'PENDING': return 'status-pending';
      default: return 'status-error';
    }
  };

  // Obtener texto del estado
  const getStatusText = (status) => {
    switch (status) {
      case 'CONFIRMED': return '✅ Confirmado';
      case 'RECEIVED_PARTIAL': return '⚠️ Parcial';
      case 'PENDING': return '⏳ Pendiente';
      default: return '❌ Error';
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1>🏦 ZatoBox Payments - Sistema Bitcoin</h1>
          <p>Sistema de gestión de pagos Bitcoin con direcciones únicas</p>
        </div>
      </header>

      {/* Alertas */}
      {alert.show && (
        <div className={`alert alert-${alert.type}`}>
          <span>{alert.message}</span>
          <button onClick={() => setAlert({ show: false, type: '', message: '' })}>
            ✕
          </button>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Procesando...</p>
          </div>
        </div>
      )}

      <main className="main">
        <div className="container">
          {/* Dashboard Stats */}
          <section className="stats-section">
            <h2>📊 Dashboard</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📈</div>
                <div className="stat-content">
                  <div className="stat-number">{stats.totalRecords}</div>
                  <div className="stat-label">Total Pagos</div>
                </div>
              </div>
              <div className="stat-card confirmed">
                <div className="stat-icon">✅</div>
                <div className="stat-content">
                  <div className="stat-number">{stats.confirmedPayments}</div>
                  <div className="stat-label">Confirmados</div>
                </div>
              </div>
              <div className="stat-card pending">
                <div className="stat-icon">⏳</div>
                <div className="stat-content">
                  <div className="stat-number">{stats.pendingPayments}</div>
                  <div className="stat-label">Pendientes</div>
                </div>
              </div>
              <div className="stat-card partial">
                <div className="stat-icon">⚠️</div>
                <div className="stat-content">
                  <div className="stat-number">{stats.partialPayments}</div>
                  <div className="stat-label">Parciales</div>
                </div>
              </div>
            </div>
          </section>

          {/* Actions */}
          <section className="actions-section">
            <div className="actions-bar">
              <button 
                className="btn btn-primary"
                onClick={() => setShowCreateModal(true)}
              >
                ➕ Crear Nuevo Pago
              </button>
              <button 
                className="btn btn-secondary"
                onClick={loadPayments}
              >
                🔄 Actualizar Lista
              </button>
            </div>
          </section>

          {/* Payments List */}
          <section className="payments-section">
            <h2>💳 Lista de Pagos</h2>
            {payments.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <h3>No hay pagos registrados</h3>
                <p>Crea tu primer pago Bitcoin para comenzar</p>
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowCreateModal(true)}
                >
                  ➕ Crear Primer Pago
                </button>
              </div>
            ) : (
              <div className="payments-grid">
                {payments.map((payment, index) => (
                  <div key={index} className="payment-card">
                    <div className="payment-header">
                      <h3>🏷️ {payment.ventaId}</h3>
                      <span className={`status ${getStatusClass(payment.status)}`}>
                        {getStatusText(payment.status)}
                      </span>
                    </div>

                    <div className="payment-details">
                      <div className="detail-row">
                        <span className="label">📍 Dirección:</span>
                        <span className="value address" title={payment.bitcoinAddress}>
                          {payment.bitcoinAddress.substring(0, 20)}...
                        </span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="label">💰 Esperado:</span>
                        <span className="value">{formatBTC(payment.expectedAmountSatoshi)} BTC</span>
                      </div>
                      
                      <div className="detail-row">
                        <span className="label">📊 Recibido:</span>
                        <span className="value">{formatBTC(payment.receivedAmountSatoshi)} BTC</span>
                      </div>

                      <div className="detail-row">
                        <span className="label">📅 Creado:</span>
                        <span className="value">
                          {new Date(Number(payment.createdAt) / 1000000).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    <div className="payment-actions">
                      <button 
                        className="btn btn-small btn-info"
                        onClick={() => {
                          setSelectedPayment(payment);
                          setShowDetailsModal(true);
                        }}
                      >
                        👁️ Ver Detalles
                      </button>
                      
                      <button 
                        className="btn btn-small btn-secondary"
                        onClick={() => checkPaymentStatus(payment.ventaId)}
                      >
                        🔍 Verificar Estado
                      </button>
                      
                      <button 
                        className="btn btn-small btn-warning"
                        onClick={() => {
                          setSelectedPayment(payment);
                          setShowSimulateModal(true);
                        }}
                      >
                        🎮 Simular Pago
                      </button>
                      
                      <button 
                        className="btn btn-small btn-danger"
                        onClick={() => deletePayment(payment.ventaId)}
                      >
                        🗑️ Eliminar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Modal: Crear Nuevo Pago */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>➕ Crear Nuevo Pago Bitcoin</h3>
              <button 
                className="modal-close"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>🏷️ ID de Venta</label>
                <input
                  type="text"
                  placeholder="Ej: VENTA001, ORDER123, etc."
                  value={newPayment.ventaId}
                  onChange={(e) => setNewPayment({...newPayment, ventaId: e.target.value})}
                />
              </div>
              
              <div className="form-group">
                <label>💰 Monto Esperado (BTC)</label>
                <input
                  type="number"
                  step="0.00000001"
                  placeholder="Ej: 0.001"
                  value={newPayment.expectedAmount}
                  onChange={(e) => setNewPayment({...newPayment, expectedAmount: e.target.value})}
                />
                <small>Equivalente a {newPayment.expectedAmount ? Math.floor(parseFloat(newPayment.expectedAmount || 0) * 100000000) : 0} satoshis</small>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                Cancelar
              </button>
              <button 
                className="btn btn-primary"
                onClick={createPayment}
              >
                🚀 Generar Dirección
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Detalles del Pago */}
      {showDetailsModal && selectedPayment && (
        <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
          <div className="modal modal-large" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>👁️ Detalles del Pago: {selectedPayment.ventaId}</h3>
              <button 
                className="modal-close"
                onClick={() => setShowDetailsModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="details-grid">
                <div className="detail-card">
                  <h4>📋 Información General</h4>
                  <div className="detail-item">
                    <strong>ID de Venta:</strong> {selectedPayment.ventaId}
                  </div>
                  <div className="detail-item">
                    <strong>Estado:</strong> 
                    <span className={`status ${getStatusClass(selectedPayment.status)}`}>
                      {getStatusText(selectedPayment.status)}
                    </span>
                  </div>
                </div>

                <div className="detail-card">
                  <h4>💰 Información Financiera</h4>
                  <div className="detail-item">
                    <strong>Monto Esperado:</strong> {formatBTC(selectedPayment.expectedAmountSatoshi)} BTC
                  </div>
                  <div className="detail-item">
                    <strong>Monto Recibido:</strong> {formatBTC(selectedPayment.receivedAmountSatoshi)} BTC
                  </div>
                  <div className="detail-item">
                    <strong>Satoshis Esperados:</strong> {selectedPayment.expectedAmountSatoshi.toString()}
                  </div>
                  <div className="detail-item">
                    <strong>Satoshis Recibidos:</strong> {selectedPayment.receivedAmountSatoshi.toString()}
                  </div>
                </div>

                <div className="detail-card full-width">
                  <h4>📍 Dirección Bitcoin</h4>
                  <div className="bitcoin-address">
                    <code>{selectedPayment.bitcoinAddress}</code>
                    <button 
                      className="btn btn-small btn-secondary"
                      onClick={() => navigator.clipboard.writeText(selectedPayment.bitcoinAddress)}
                    >
                      📋 Copiar
                    </button>
                  </div>
                </div>

                <div className="detail-card">
                  <h4>📅 Fechas</h4>
                  <div className="detail-item">
                    <strong>Creado:</strong> {new Date(Number(selectedPayment.createdAt) / 1000000).toLocaleString()}
                  </div>
                  <div className="detail-item">
                    <strong>Actualizado:</strong> {new Date(Number(selectedPayment.updatedAt) / 1000000).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowDetailsModal(false)}
              >
                Cerrar
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => checkPaymentStatus(selectedPayment.ventaId)}
              >
                🔄 Actualizar Estado
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Simular Pago */}
      {showSimulateModal && selectedPayment && (
        <div className="modal-overlay" onClick={() => setShowSimulateModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🎮 Simular Pago: {selectedPayment.ventaId}</h3>
              <button 
                className="modal-close"
                onClick={() => setShowSimulateModal(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="modal-body">
              <div className="simulation-info">
                <p>💡 Esta función simula un pago llegando a la dirección Bitcoin.</p>
                <p>📍 <strong>Dirección:</strong> {selectedPayment.bitcoinAddress}</p>
                <p>💰 <strong>Esperado:</strong> {formatBTC(selectedPayment.expectedAmountSatoshi)} BTC</p>
              </div>
              
              <div className="form-group">
                <label>💸 Monto a Simular (BTC)</label>
                <input
                  type="number"
                  step="0.00000001"
                  placeholder="Ej: 0.001"
                  value={simulateAmount}
                  onChange={(e) => setSimulateAmount(e.target.value)}
                />
                <small>Equivalente a {simulateAmount ? Math.floor(parseFloat(simulateAmount || 0) * 100000000) : 0} satoshis</small>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowSimulateModal(false)}
              >
                Cancelar
              </button>
              <button 
                className="btn btn-warning"
                onClick={simulatePayment}
              >
                🎮 Simular Pago
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;