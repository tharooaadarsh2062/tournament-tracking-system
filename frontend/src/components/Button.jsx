import React from 'react';
export default function Button({ children, ...props }) { return <button className='bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded' {...props}>{children}</button>; }
