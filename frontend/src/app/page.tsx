'use client'

import React, { useState, useEffect } from 'react'
import { DollarSign, PieChart, TrendingUp, FileText, Settings, Plus, Edit, Trash2, RotateCcw, Check, X, Link } from 'lucide-react'
import { SimpleFINSetup } from '../components'

// Mock data - in real app this would come from API
const mockBudgetData = {
  period: {
    id: '1',
    name: 'January 2024',
    totalIncome: 5000,
    totalAllocated: 4800,
    totalSpent: 3200
  },
  categories: [
    {
      id: '1',
      name: 'Housing',
      items: [
        { id: '1', name: 'Rent/Mortgage', allocated: 1200, spent: 1200, rollover: 0, rolloverEnabled: false },
        { id: '2', name: 'Utilities', allocated: 200, spent: 185, rollover: 0, rolloverEnabled: true },
        { id: '3', name: 'Internet', allocated: 80, spent: 79.99, rollover: 0, rolloverEnabled: false }
      ]
    },
    {
      id: '2',
      name: 'Food',
      items: [
        { id: '4', name: 'Groceries', allocated: 400, spent: 320, rollover: 50, rolloverEnabled: true },
        { id: '5', name: 'Restaurants', allocated: 200, spent: 180, rollover: 20, rolloverEnabled: true }
      ]
    },
    {
      id: '3',
      name: 'Transportation',
      items: [
        { id: '6', name: 'Gas', allocated: 150, spent: 140, rollover: 0, rolloverEnabled: true },
        { id: '7', name: 'Car Insurance', allocated: 120, spent: 120, rollover: 0, rolloverEnabled: false }
      ]
    },
    {
      id: '4',
      name: 'Personal',
      items: [
        { id: '8', name: 'Entertainment', allocated: 150, spent: 95, rollover: 25, rolloverEnabled: true },
        { id: '9', name: 'Clothing', allocated: 100, spent: 60, rollover: 0, rolloverEnabled: false }
      ]
    }
  ]
}

interface BudgetItem {
  id: string
  name: string
  allocated: number
  spent: number
  rollover: number
  rolloverEnabled: boolean
}

interface BudgetCategory {
  id: string
  name: string
  items: BudgetItem[]
}

interface EditingItem {
  categoryId: string
  itemId: string
  field: 'name' | 'allocated'
  value: string
}

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('budget')
  const [budgetData, setBudgetData] = useState(mockBudgetData)
  const [editingItem, setEditingItem] = useState<EditingItem | null>(null)
  const [newItemCategory, setNewItemCategory] = useState<string | null>(null)
  const [newItemName, setNewItemName] = useState('')
  const [newItemAmount, setNewItemAmount] = useState('')

  const calculateCategoryTotals = (category: BudgetCategory) => {
    const allocated = category.items.reduce((sum, item) => sum + item.allocated + item.rollover, 0)
    const spent = category.items.reduce((sum, item) => sum + item.spent, 0)
    const remaining = allocated - spent
    return { allocated, spent, remaining }
  }

  const calculateOverallTotals = () => {
    let totalAllocated = 0
    let totalSpent = 0
    
    budgetData.categories.forEach(category => {
      const totals = calculateCategoryTotals(category)
      totalAllocated += totals.allocated
      totalSpent += totals.spent
    })
    
    return {
      totalAllocated,
      totalSpent,
      remaining: budgetData.period.totalIncome - totalAllocated,
      leftToBudget: budgetData.period.totalIncome - totalAllocated
    }
  }

  const handleEditStart = (categoryId: string, itemId: string, field: 'name' | 'allocated', currentValue: string | number) => {
    setEditingItem({ categoryId, itemId, field, value: currentValue.toString() })
  }

  const handleEditSave = () => {
    if (!editingItem) return
    
    setBudgetData(prev => ({
      ...prev,
      categories: prev.categories.map(category => 
        category.id === editingItem.categoryId
          ? {
              ...category,
              items: category.items.map(item => 
                item.id === editingItem.itemId
                  ? {
                      ...item,
                      [editingItem.field]: editingItem.field === 'allocated' 
                        ? parseFloat(editingItem.value) || 0
                        : editingItem.value
                    }
                  : item
              )
            }
          : category
      )
    }))
    
    setEditingItem(null)
  }

  const handleEditCancel = () => {
    setEditingItem(null)
  }

  const toggleRollover = (categoryId: string, itemId: string) => {
    setBudgetData(prev => ({
      ...prev,
      categories: prev.categories.map(category => 
        category.id === categoryId
          ? {
              ...category,
              items: category.items.map(item => 
                item.id === itemId
                  ? { ...item, rolloverEnabled: !item.rolloverEnabled }
                  : item
              )
            }
          : category
      )
    }))
  }

  const addNewItem = (categoryId: string) => {
    if (!newItemName || !newItemAmount) return
    
    const newItem: BudgetItem = {
      id: Date.now().toString(),
      name: newItemName,
      allocated: parseFloat(newItemAmount) || 0,
      spent: 0,
      rollover: 0,
      rolloverEnabled: false
    }
    
    setBudgetData(prev => ({
      ...prev,
      categories: prev.categories.map(category => 
        category.id === categoryId
          ? { ...category, items: [...category.items, newItem] }
          : category
      )
    }))
    
    setNewItemCategory(null)
    setNewItemName('')
    setNewItemAmount('')
  }

  const deleteItem = (categoryId: string, itemId: string) => {
    setBudgetData(prev => ({
      ...prev,
      categories: prev.categories.map(category => 
        category.id === categoryId
          ? { ...category, items: category.items.filter(item => item.id !== itemId) }
          : category
      )
    }))
  }

  const overallTotals = calculateOverallTotals()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">Home Budget</span>
            </div>
            <div className="flex items-center space-x-4">
              <button className="btn-primary">
                <Plus className="h-4 w-4 mr-2" />
                Add Transaction
              </button>
              <Settings className="h-6 w-6 text-gray-500 cursor-pointer hover:text-gray-700" />
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'budget', name: 'Budget', icon: PieChart },
                { id: 'transactions', name: 'Transactions', icon: DollarSign },
                { id: 'reports', name: 'Reports', icon: TrendingUp },
                { id: 'documents', name: 'Documents', icon: FileText },
                { id: 'integrations', name: 'Integrations', icon: Link },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Budget Tab - EveryDollar Style */}
        {activeTab === 'budget' && (
          <div className="space-y-6">
            {/* Budget Header */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">{budgetData.period.name}</h1>
                <div className="flex space-x-3">
                  <button className="btn-secondary">Previous Month</button>
                  <button className="btn-primary">
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Create Next Month with Rollover
                  </button>
                </div>
              </div>
              
              {/* Budget Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    ${budgetData.period.totalIncome.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">Monthly Income</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    ${overallTotals.totalAllocated.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">Budgeted</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    ${overallTotals.totalSpent.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">Spent</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${
                    overallTotals.leftToBudget >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${Math.abs(overallTotals.leftToBudget).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">
                    {overallTotals.leftToBudget >= 0 ? 'Left to Budget' : 'Over Budget'}
                  </div>
                </div>
              </div>
            </div>

            {/* Budget Categories */}
            <div className="space-y-4">
              {budgetData.categories.map((category) => {
                const categoryTotals = calculateCategoryTotals(category)
                
                return (
                  <div key={category.id} className="bg-white rounded-lg shadow-sm border">
                    {/* Category Header */}
                    <div className="bg-gray-50 px-6 py-4 border-b">
                      <div className="flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                        <div className="flex items-center space-x-4 text-sm">
                          <span className="text-gray-600">
                            Budgeted: ${categoryTotals.allocated.toLocaleString()}
                          </span>
                          <span className="text-gray-600">
                            Spent: ${categoryTotals.spent.toLocaleString()}
                          </span>
                          <span className={`font-semibold ${
                            categoryTotals.remaining >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            Remaining: ${categoryTotals.remaining.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Budget Items */}
                    <div className="divide-y divide-gray-100">
                      {category.items.map((item) => {
                        const available = item.allocated + item.rollover
                        const remaining = available - item.spent
                        const percentage = available > 0 ? (item.spent / available) * 100 : 0
                        
                        return (
                          <div key={item.id} className="p-4 hover:bg-gray-50">
                            <div className="flex items-center justify-between">
                              {/* Item Name */}
                              <div className="flex-1">
                                {editingItem?.categoryId === category.id && editingItem?.itemId === item.id && editingItem?.field === 'name' ? (
                                  <div className="flex items-center space-x-2">
                                    <input
                                      type="text"
                                      value={editingItem.value}
                                      onChange={(e) => setEditingItem({...editingItem, value: e.target.value})}
                                      className="input w-48"
                                      autoFocus
                                    />
                                    <button onClick={handleEditSave} className="text-green-600 hover:text-green-700">
                                      <Check className="h-4 w-4" />
                                    </button>
                                    <button onClick={handleEditCancel} className="text-red-600 hover:text-red-700">
                                      <X className="h-4 w-4" />
                                    </button>
                                  </div>
                                ) : (
                                  <div className="flex items-center space-x-2">
                                    <span className="font-medium text-gray-900">{item.name}</span>
                                    <button 
                                      onClick={() => handleEditStart(category.id, item.id, 'name', item.name)}
                                      className="text-gray-400 hover:text-gray-600"
                                    >
                                      <Edit className="h-3 w-3" />
                                    </button>
                                  </div>
                                )}
                              </div>
                              
                              {/* Budget Amount */}
                              <div className="flex items-center space-x-4">
                                {editingItem?.categoryId === category.id && editingItem?.itemId === item.id && editingItem?.field === 'allocated' ? (
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-500">$</span>
                                    <input
                                      type="number"
                                      value={editingItem.value}
                                      onChange={(e) => setEditingItem({...editingItem, value: e.target.value})}
                                      className="input w-24 text-right"
                                      autoFocus
                                    />
                                    <button onClick={handleEditSave} className="text-green-600 hover:text-green-700">
                                      <Check className="h-4 w-4" />
                                    </button>
                                    <button onClick={handleEditCancel} className="text-red-600 hover:text-red-700">
                                      <X className="h-4 w-4" />
                                    </button>
                                  </div>
                                ) : (
                                  <div className="flex items-center space-x-2">
                                    <span className="text-sm text-gray-600 w-20 text-right">
                                      ${item.allocated.toLocaleString()}
                                    </span>
                                    <button 
                                      onClick={() => handleEditStart(category.id, item.id, 'allocated', item.allocated)}
                                      className="text-gray-400 hover:text-gray-600"
                                    >
                                      <Edit className="h-3 w-3" />
                                    </button>
                                  </div>
                                )}
                                
                                {/* Rollover */}
                                {item.rollover > 0 && (
                                  <span className="text-sm text-blue-600 w-16 text-right">
                                    +${item.rollover}
                                  </span>
                                )}
                                
                                {/* Spent */}
                                <span className="text-sm text-gray-600 w-20 text-right">
                                  ${item.spent.toLocaleString()}
                                </span>
                                
                                {/* Remaining */}
                                <span className={`text-sm font-medium w-20 text-right ${
                                  remaining >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  ${Math.abs(remaining).toLocaleString()}
                                </span>
                                
                                {/* Rollover Toggle */}
                                <button
                                  onClick={() => toggleRollover(category.id, item.id)}
                                  className={`px-2 py-1 rounded text-xs font-medium ${
                                    item.rolloverEnabled 
                                      ? 'bg-blue-100 text-blue-800 hover:bg-blue-200' 
                                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                  }`}
                                >
                                  {item.rolloverEnabled ? 'Rollover ON' : 'Rollover OFF'}
                                </button>
                                
                                {/* Delete */}
                                <button 
                                  onClick={() => deleteItem(category.id, item.id)}
                                  className="text-gray-400 hover:text-red-600"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </div>
                            
                            {/* Progress Bar */}
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${
                                    percentage > 100 ? 'bg-red-500' : percentage > 80 ? 'bg-yellow-500' : 'bg-green-500'
                                  }`}
                                  style={{ width: `${Math.min(percentage, 100)}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        )
                      })}
                      
                      {/* Add New Item */}
                      {newItemCategory === category.id ? (
                        <div className="p-4 bg-blue-50 border-t">
                          <div className="flex items-center space-x-4">
                            <input
                              type="text"
                              placeholder="Item name"
                              value={newItemName}
                              onChange={(e) => setNewItemName(e.target.value)}
                              className="input flex-1"
                            />
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-500">$</span>
                              <input
                                type="number"
                                placeholder="0"
                                value={newItemAmount}
                                onChange={(e) => setNewItemAmount(e.target.value)}
                                className="input w-24 text-right"
                              />
                            </div>
                            <button 
                              onClick={() => addNewItem(category.id)}
                              className="btn-success"
                            >
                              Add
                            </button>
                            <button 
                              onClick={() => setNewItemCategory(null)}
                              className="btn-secondary"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="p-4">
                          <button 
                            onClick={() => setNewItemCategory(category.id)}
                            className="flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium"
                          >
                            <Plus className="h-4 w-4 mr-1" />
                            Add Budget Item
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Other tabs */}
        {activeTab === 'transactions' && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Transactions</h3>
            </div>
            <div className="card-content">
              <p className="text-gray-500">Transaction management coming soon...</p>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Reports & Analytics</h3>
            </div>
            <div className="card-content">
              <p className="text-gray-500">Reporting features coming soon...</p>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Document Storage</h3>
            </div>
            <div className="card-content">
              <p className="text-gray-500">Secure document storage coming soon...</p>
            </div>
          </div>
        )}

        {activeTab === 'integrations' && (
          <div className="space-y-6">
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Bank Account Integration</h3>
              </div>
              <div className="card-content">
                <SimpleFINSetup />
              </div>
            </div>
            
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Other Integrations</h3>
              </div>
              <div className="card-content">
                <p className="text-gray-500">QuickBooks sync and other integrations coming soon...</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
