import { useState } from 'react'

type Status = 'Scheduled' | 'Completed' | 'Cancelled'

interface Appointment {
  id: number
  patient: string
  doctor: string
  date: string
  time: string
  status: Status
  type: string
}

const initialAppointments: Appointment[] = [
  { id: 1, patient: 'Alice Johnson', doctor: 'Dr. Smith', date: '2026-04-03', time: '09:00', status: 'Scheduled', type: 'General Checkup' },
  { id: 2, patient: 'Bob Williams', doctor: 'Dr. Patel', date: '2026-04-03', time: '10:30', status: 'Scheduled', type: 'Cardiology' },
  { id: 3, patient: 'Carol Davis', doctor: 'Dr. Lee', date: '2026-04-02', time: '14:00', status: 'Completed', type: 'Dermatology' },
  { id: 4, patient: 'David Brown', doctor: 'Dr. Smith', date: '2026-04-01', time: '11:00', status: 'Cancelled', type: 'Neurology' },
  { id: 5, patient: 'Eva Martinez', doctor: 'Dr. Patel', date: '2026-04-04', time: '15:30', status: 'Scheduled', type: 'Pediatrics' },
]

const statusStyles: Record<Status, string> = {
  Scheduled: 'bg-blue-100 text-blue-700',
  Completed: 'bg-green-100 text-green-700',
  Cancelled: 'bg-red-100 text-red-700',
}

export default function Appointments() {
  const [appointments] = useState<Appointment[]>(initialAppointments)
  const [filter, setFilter] = useState<Status | 'All'>('All')

  const filtered = filter === 'All' ? appointments : appointments.filter((a) => a.status === filter)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Appointments</h1>
          <p className="mt-1 text-gray-500">Manage patient appointments</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          + New Appointment
        </button>
      </div>

      <div className="flex gap-2">
        {(['All', 'Scheduled', 'Completed', 'Cancelled'] as const).map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === s ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Patient', 'Doctor', 'Date', 'Time', 'Type', 'Status'].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map((a) => (
              <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 font-medium text-gray-900">{a.patient}</td>
                <td className="px-4 py-3 text-gray-600">{a.doctor}</td>
                <td className="px-4 py-3 text-gray-600">{a.date}</td>
                <td className="px-4 py-3 text-gray-600">{a.time}</td>
                <td className="px-4 py-3 text-gray-600">{a.type}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[a.status]}`}>
                    {a.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-400">No appointments found.</div>
        )}
      </div>
    </div>
  )
}
