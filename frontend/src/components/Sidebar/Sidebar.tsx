import React, { FC } from 'react';
import './Sidebar.css';

interface SidebarProps {
  children: React.ReactNode
}

const Sidebar: FC<SidebarProps> = ({children}) => (
<div className="container-fluid">
    <div className="row">
        <div className="col-sm-auto bg-light sticky-top">
            <div className="d-flex flex-sm-column flex-row flex-nowrap bg-light align-items-center sticky-top">
                <a href="/" className="d-block p-3 link-dark text-decoration-none" title="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Icon-only">
                    <i className="bi-bootstrap fs-1"></i>
                </a>
                <ul className="nav nav-pills nav-flush flex-sm-column flex-row flex-nowrap mb-auto mx-auto text-center justify-content-between w-100 px-3 align-items-center">
                    <li className="nav-item">
                        <a href="#" className="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Home">
                            <i className="bi-house fs-1"></i>
                        </a>
                    </li>
                    <li>
                        <a href="#" className="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Dashboard">
                            <i className="bi-speedometer2 fs-1"></i>
                        </a>
                    </li>
                    <li>
                        <a href="#" className="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Orders">
                            <i className="bi-table fs-1"></i>
                        </a>
                    </li>
                    <li>
                        <a href="#" className="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Products">
                            <i className="bi-heart fs-1"></i>
                        </a>
                    </li>
                    <li>
                        <a href="#" className="nav-link py-3 px-2" title="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Customers">
                            <i className="bi-people fs-1"></i>
                        </a>
                    </li>
                </ul>
            </div>
        </div>
        <div className="col-sm p-3 min-vh-100">
            {/* content */}
            {children}
        </div>
    </div>
</div>
);

export default Sidebar;
