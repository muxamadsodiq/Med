interface Doctor {
  id: number
  name: string
  specialty: string
  experience: string
  patients: number
  rating: number
  available: boolean
  avatar: string
}

const doctors: Doctor[] = [
  { id: 1, name: 'Dr. James Smith', specialty: 'General Practitioner', experience: '12 years', patients: 340, rating: 4.8, available: true, avatar: '👨‍⚕️' },
  { id: 2, name: 'Dr. Priya Patel', specialty: 'Cardiologist', experience: '9 years', patients: 210, rating: 4.9, available: true, avatar: '👩‍⚕️' },
  { id: 3, name: 'Dr. Kevin Lee', specialty: 'Dermatologist', experience: '7 years', patients: 185, rating: 4.7, available: false, avatar: '👨‍⚕️' },
  { id: 4, name: 'Dr. Sara Ahmed', specialty: 'Neurologist', experience: '15 years', patients: 290, rating: 4.9, available: true, avatar: '👩‍⚕️' },
  { id: 5, name: 'Dr. Tom Nguyen', specialty: 'Pediatrician', experience: '11 years', patients: 420, rating: 4.8, available: true, avatar: '👨‍⚕️' },
  { id: 6, name: 'Dr. Maria Lopez', specialty: 'Orthopedics', experience: '8 years', patients: 160, rating: 4.6, available: false, avatar: '👩‍⚕️' },
]

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="flex items-center gap-1 text-sm text-yellow-500 font-medium">
      ★ {rating}
    </span>
  )
}

export default function Doctors() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Doctors</h1>
          <p className="mt-1 text-gray-500">Our medical professionals</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          + Add Doctor
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {doctors.map((doc) => (
          <div key={doc.id} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-4xl">{doc.avatar}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{doc.name}</h3>
                  <p className="text-sm text-blue-600">{doc.specialty}</p>
                </div>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${doc.available ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                {doc.available ? 'Available' : 'Busy'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm text-gray-500 border-t border-gray-100 pt-3 mt-3">
              <span>🩺 {doc.experience}</span>
              <span>👥 {doc.patients} patients</span>
              <StarRating rating={doc.rating} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
