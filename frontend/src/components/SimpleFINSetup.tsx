'use client'

import React, { useState, useEffect } from 'react'
import { Link, RefreshCw, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react'

interface SimpleFINStatus {
  connected: boolean
  access_url_configured: boolean
}

interface SimpleFINSetupProps {
  onConnectionChange?: (connected: boolean) => void
}

export default function SimpleFINSetup({ onConnectionChange }: SimpleFINSetupProps) {
  const [status, setStatus] = useState<SimpleFINStatus>({ connected: false, access_url_configured: false })
  const [setupToken, setSetupToken] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    checkStatus()
  }, [])

  const checkStatus = async () => {
    try {
      const response = await fetch('/api/simplefin/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
        onConnectionChange?.(data.connected)
      }
    } catch (err) {
      console.error('Failed to check SimpleFIN status:', err)
    }
  }

  const setupConnection = async () => {
    if (!setupToken.trim()) {
      setError('Please enter a setup token')
      return
    }

    setIsLoading(true)
    setError('')
    setMessage('')

    try {
      const response = await fetch('/api/simplefin/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ setup_token: setupToken })
      })

      const data = await response.json()

      if (response.ok) {
        setMessage(data.message)
        setSetupToken('')
        await checkStatus()
      } else {
        setError(data.detail || 'Failed to setup SimpleFIN connection')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const syncTransactions = async () => {
    setIsSyncing(true)
    setError('')
    setMessage('')

    try {
      const response = await fetch('/api/simplefin/sync', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      const data = await response.json()

      if (response.ok) {
        setMessage(data.message)
      } else {
        setError(data.detail || 'Failed to sync transactions')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsSyncing(false)
    }
  }

  const disconnect = async () => {
    if (!confirm('Are you sure you want to disconnect SimpleFIN? This will remove your connection but keep existing transactions.')) {
      return
    }

    try {
      const response = await fetch('/api/simplefin/disconnect', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        setMessage('SimpleFIN connection removed successfully')
        await checkStatus()
      } else {
        setError('Failed to disconnect SimpleFIN')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Link className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">SimpleFIN Integration</h3>
        </div>
        
        {status.connected && (
          <div className="flex items-center space-x-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="text-sm font-medium">Connected</span>
          </div>
        )}
      </div>

      {/* Status Messages */}
      {message && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-700">{message}</p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-start space-x-2">
          <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {!status.connected ? (
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Connect your bank accounts through SimpleFIN to automatically import transactions.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
              <div className="flex items-start space-x-2">
                <ExternalLink className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm text-blue-700 font-medium">Get Your Setup Token</p>
                  <p className="text-sm text-blue-600 mt-1">
                    Visit{' '}
                    <a 
                      href="https://bridge.simplefin.org/simplefin/create" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="underline hover:text-blue-800"
                    >
                      SimpleFIN Bridge
                    </a>
                    {' '}to connect your bank and get a setup token.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="setupToken" className="block text-sm font-medium text-gray-700 mb-2">
              Setup Token
            </label>
            <textarea
              id="setupToken"
              value={setupToken}
              onChange={(e) => setSetupToken(e.target.value)}
              placeholder="Paste your SimpleFIN setup token here..."
              className="input w-full h-24 resize-none"
              disabled={isLoading}
            />
          </div>

          <button
            onClick={setupConnection}
            disabled={isLoading || !setupToken.trim()}
            className="btn-primary w-full"
          >
            {isLoading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Setting up connection...
              </>
            ) : (
              'Connect SimpleFIN'
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Your SimpleFIN connection is active. You can now sync transactions from your connected accounts.
          </p>

          <div className="flex space-x-3">
            <button
              onClick={syncTransactions}
              disabled={isSyncing}
              className="btn-primary flex-1"
            >
              {isSyncing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Sync Transactions
                </>
              )}
            </button>

            <button
              onClick={disconnect}
              className="btn-secondary"
            >
              Disconnect
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
