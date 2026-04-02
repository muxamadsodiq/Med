import { useState } from 'react'

interface Patient {
  id: number
  name: string
  age: number
  gender: string
  bloodType: string
  phone: string
  lastVisit: string
  condition: string
}

const patients: Patient[] = [
  { id: 1, name: 'Alice Johnson', age: 34, gender: 'Female', bloodType: 'A+', phone: '555-0101', lastVisit: '2026-04-02', condition: 'Hypertension' },
  { id: 2, name: 'Bob Williams', age: 58, gender: 'Male', bloodType: 'O-', phone: '555-0102', lastVisit: '2026-04-03', condition: 'Diabetes' },
  { id: 3, name: 'Carol Davis', age: 27, gender: 'Female', bloodType: 'B+', phone: '555-0103', lastVisit: '2026-04-02', condition: 'Eczema' },
  { id: 4, name: 'David Brown', age: 45, gender: 'Male', bloodType: 'AB+', phone: '555-0104', lastVisit: '2026-04-01', condition: 'Migraine' },
  { id: 5, name: 'Eva Martinez', age: 8, gender: 'Female', bloodType: 'O+', phone: '555-0105', lastVisit: '2026-04-04', condition: 'Asthma' },
  { id: 6, name: 'Frank Wilson', age: 71, gender: 'Male', bloodType: 'A-', phone: '555-0106', lastVisit: '2026-03-28', condition: 'Arthritis' },
]

export default function Patients() {
  const [search, setSearch] = useState('')

  const filtered = patients.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.condition.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Patients</h1>
          <p className="mt-1 text-gray-500">Manage patient records</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          + Add Patient
        </button>
      </div>

      <input
        type="text"
        placeholder="Search by name or condition…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full sm:w-80 px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
      />

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Name', 'Age', 'Gender', 'Blood Type', 'Phone', 'Last Visit', 'Condition'].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 font-medium text-gray-900">{p.name}</td>
                <td className="px-4 py-3 text-gray-600">{p.age}</td>
                <td className="px-4 py-3 text-gray-600">{p.gender}</td>
                <td className="px-4 py-3">
                  <span className="bg-red-50 text-red-700 text-xs font-medium px-2 py-0.5 rounded">
                    {p.bloodType}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{p.phone}</td>
                <td className="px-4 py-3 text-gray-600">{p.lastVisit}</td>
                <td className="px-4 py-3 text-gray-600">{p.condition}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-400">No patients found.</div>
        )}
      </div>
    </div>
  )
}
